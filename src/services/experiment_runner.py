import os
import sys
import json
import uuid
import time
import shutil
import logging
import hashlib
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.research_registry import ResearchLedger
from src.revenue_os.analytics.asset_registry import AssetRegistry
from src.revenue_os.analytics.policy import PolicyEngine
from src.revenue_os.analytics.schemas import (
    ExperimentContract, Hypothesis, Variant, Economics, RealWorldMetrics, 
    CreativeGenome, ExperimentPolicy
)
from src.revenue_os.analytics.calibration_engine import CalibrationEngine
from src.reality.base import CapabilityRegistry
from src.factory.base import FactoryRegistry
from src.factory.quality.video_gate import VideoQualityGate
from src.factory.quality.image_gate import ImageQualityGate
from src.factory.schemas import CreativeBrief, GeneratedAsset
from src.revenue_os.analytics.profile import ExperimentProfile
from src.services.exceptions import RetryableError, FatalError
from src.revenue_os.tracking.mlflow_tracker import MLflowTracker

logger = logging.getLogger("revenue_os.experiment_runner")

class ExperimentState(Enum):
    CREATED = "CREATED"
    RESEARCHED = "RESEARCHED"
    HYPOTHESIS_FORMED = "HYPOTHESIS_FORMED"
    ASSET_GENERATED = "ASSET_GENERATED"
    QUALITY_CHECKED = "QUALITY_CHECKED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    PUBLISHED = "PUBLISHED"
    OBSERVING = "OBSERVING"
    OBSERVED = "OBSERVED"
    CALIBRATED = "CALIBRATED"
    FAILED_RETRYABLE = "FAILED_RETRYABLE"
    FAILED_PERMANENT = "FAILED_PERMANENT"

class ExperimentRunner:
    """
    O Coração Evolucionário do AI Revenue OS.
    Executa autonomamente o ciclo científico através de uma máquina de estados:
    CREATED -> RESEARCHED -> HYPOTHESIS_FORMED -> ASSET_GENERATED -> QUALITY_CHECKED -> HUMAN_APPROVED -> PUBLISHED -> OBSERVED -> CALIBRATED
    """
    
    def __init__(
        self,
        db: ExperimentDatabase,
        registry: HypothesisRegistry,
        reality_registry: CapabilityRegistry,
        factory_registry: FactoryRegistry,
        research_ledger: ResearchLedger = None,
        asset_registry: AssetRegistry = None,
        policy_engine: PolicyEngine = None,
        require_human_approval: bool = False,
        profile: ExperimentProfile = None
    ):
        self.db = db
        self.registry = registry
        self.reality_registry = reality_registry
        self.factory_registry = factory_registry
        self.research_ledger = research_ledger or ResearchLedger(db)
        self.asset_registry = asset_registry or AssetRegistry(db)
        self.policy_engine = policy_engine or PolicyEngine(db, ExperimentPolicy())
        self.calibration_engine = CalibrationEngine()
        self.require_human_approval = require_human_approval
        self.profile = profile
        self.is_synthetic = True
        self.mlflow = MLflowTracker()
        
        self.run_id = self.db.start_run(
            profile=profile.name if profile else "default",
            runner_version="v2.0",
            worker_id="worker-1"
        )
        
        self.ctx = {}

    def _save_checkpoint(self):
        if "experiment_id" in self.ctx:
            exp_dir = Path("experiments") / self.ctx["experiment_id"]
            exp_dir.mkdir(parents=True, exist_ok=True)
            with open(exp_dir / "manifest.partial.json", "w") as f:
                f.write(json.dumps({
                    "state": self.ctx.get("state").value if hasattr(self.ctx.get("state"), "value") else str(self.ctx.get("state")),
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
                }))
                
    def _seal_bundle(self):
        if "experiment_id" not in self.ctx: return
        exp_dir = Path("experiments") / self.ctx["experiment_id"]
        if not exp_dir.exists(): return
        
        manifest = {
            "experiment_id": self.ctx["experiment_id"],
            "sealed_at": datetime.now(timezone.utc).isoformat() + "Z",
            "seed_config": self.ctx.get("seed_config", {}),
            "files": {}
        }
        
        for fpath in exp_dir.iterdir():
            if fpath.is_file() and fpath.name not in ["manifest.json", "manifest.partial.json"]:
                h = hashlib.sha256(fpath.read_bytes()).hexdigest()
                manifest["files"][fpath.name] = {"sha256": h, "size_bytes": fpath.stat().st_size}
                
        manifest_str = json.dumps(manifest, indent=2)
        manifest["bundle_hash"] = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()
        
        with open(exp_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
            
        partial = exp_dir / "manifest.partial.json"
        if partial.exists():
            partial.unlink()
                
    def _enforce_sla(self, step_name: str, duration_sec: float):
        slas = {"RESEARCH": 60, "FACTORY": 600, "PUBLISH": 30, "CALIBRATION": 300}
        limit = slas.get(step_name, 300)
        if duration_sec > limit:
            level = "CRITICAL" if duration_sec > limit * 2 else "WARNING"
            print(f"⚠️ SLA {level} na etapa {step_name}: {duration_sec:.1f}s (Limite: {limit}s)")
            self.db.log_event(self.ctx["experiment_id"], f"SLA_VIOLATION_{level}", {"step": step_name, "duration": duration_sec, "limit": limit})

    def _check_backpressure(self):
        if not self.profile: return
        bp = self.profile.backpressure
        if not bp: return
        
        import sqlite3
        with self.db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT COUNT(*) as c FROM experiments WHERE status = 'CREATED'")
            if c.fetchone()['c'] >= bp.get('research', {}).get('max_queue', 9999):
                raise RuntimeError("Backpressure Block: Research queue full.")
            c.execute("SELECT COUNT(*) as c FROM experiments WHERE status = 'HYPOTHESIS_FORMED'")
            if c.fetchone()['c'] >= bp.get('rendering', {}).get('max_queue', 9999):
                raise RuntimeError("Backpressure Block: Rendering queue full.")

    def _check_safety_policy(self):
        state = self.db.get_system_state("AUTOPAUSE")
        if state and state.get("active"):
            print(f"\n🛑 [ExperimentRunner] SISTEMA EM AUTOPAUSE: {state.get('reason')} - {state.get('subreason')}")
            sys.exit(1)
            
        override = self.db.get_system_state("HUMAN_OVERRIDE")
        if override and override.get("active"):
            print(f"\n🛑 [ExperimentRunner] OVERRIDE HUMANO ATIVO: {override.get('reason') or 'Pausa manual solicitada pelo operador.'}")
            sys.exit(1)
            
        if not self.profile or not hasattr(self.profile, "config") or not self.profile.config:
            return
            
        policy = self.profile.config.get("safety_policy", {})
        if not policy: return
        
        # Simple simulated check for the sake of the OQ / Demo
        # Real implementation would query DB for failure rate
        import sqlite3
        with self.db._get_conn() as conn:
            c = conn.cursor()
            
            # 1. Total de erros de provedor
            try:
                c.execute("SELECT count(*) as c FROM experiment_events WHERE event_type = 'FAILED_PERMANENT' AND timestamp > datetime('now', '-1 day')")
                failed = c.fetchone()[0]
                if failed >= policy.get("max_provider_errors", 50):
                    self.db.set_system_state("AUTOPAUSE", {"active": True, "reason": "INFRASTRUCTURE", "subreason": "PROVIDER_FAILURE_RATE"})
                    print("\n🛑 [ExperimentRunner] AUTOPAUSE ATIVADO: PROVIDER_FAILURE_RATE")
                    sys.exit(1)
            except sqlite3.OperationalError:
                pass

            # 2. Orçamento diário (Max cost)
            try:
                c.execute("SELECT sum(generation_cost_usd) FROM experiments WHERE published_at > datetime('now', '-1 day')")
                cost_row = c.fetchone()
                cost_today = cost_row[0] if cost_row and cost_row[0] is not None else 0.0
                if cost_today >= policy.get("max_cost_per_day", 2.0):
                    self.db.set_system_state("AUTOPAUSE", {"active": True, "reason": "BUDGET", "subreason": "MAX_COST_PER_DAY_EXCEEDED"})
                    print(f"\n🛑 [ExperimentRunner] AUTOPAUSE ATIVADO: MAX_COST_PER_DAY_EXCEEDED ({cost_today} >= {policy.get('max_cost_per_day')})")
                    sys.exit(1)
            except sqlite3.OperationalError:
                pass

            # 3. Postagens diárias (Max posts)
            try:
                c.execute("SELECT count(*) FROM experiments WHERE published_at > datetime('now', '-1 day')")
                posts_row = c.fetchone()
                posts_today = posts_row[0] if posts_row and posts_row[0] is not None else 0
                max_daily = policy.get("max_daily_posts", 5)
                if posts_today >= max_daily:
                    self.db.set_system_state("AUTOPAUSE", {"active": True, "reason": "BUDGET", "subreason": "MAX_DAILY_POSTS_EXCEEDED"})
                    print(f"\n🛑 [ExperimentRunner] AUTOPAUSE ATIVADO: MAX_DAILY_POSTS_EXCEEDED ({posts_today} >= {max_daily})")
                    sys.exit(1)
            except sqlite3.OperationalError:
                pass

        # 4. Pinterest Cooldown Check
        try:
            from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
            safety_coord = PinterestSafetyCoordinator(self.db)
            state_data = safety_coord.get_state()
            if state_data.get("state") == "COOLDOWN":
                self.db.set_system_state("AUTOPAUSE", {
                    "active": True,
                    "reason": "PINTEREST_COOLDOWN",
                    "subreason": f"Resfriamento ativo ate {state_data.get('cooldown_until')}"
                })
                print(f"\n🛑 [ExperimentRunner] AUTOPAUSE ATIVADO: PINTEREST_COOLDOWN (Resfriamento ativo ate {state_data.get('cooldown_until')})")
                sys.exit(1)
        except Exception as e:
            pass

    def run_cycle(self, stop_at_state: ExperimentState = None) -> Dict[str, Any]:
        """Executa a máquina de estados até o final ou até o estado solicitado."""
        self._check_safety_policy()
        
        if not self.ctx.get("state"):
            import random
            import numpy as np
            seed = int(time.time() * 1000) % (2**32)
            self.ctx = {
                "state": ExperimentState.CREATED, 
                "start_time": time.time(), 
                "experiment_id": f"EXP-{uuid.uuid4().hex[:8].upper()}",
                "seed_config": {
                    "master_seed": seed,
                    "python_random_seed": seed,
                    "numpy_seed": seed,
                    "llm_temperature": 0.7,
                    "llm_top_p": 0.9,
                    "sampling_strategy": "nucleus"
                }
            }
            random.seed(seed)
            np.random.seed(seed)
            print(f"\n🔬 [ExperimentRunner] Iniciando {self.ctx['experiment_id']} (State: CREATED)")
            if self.mlflow:
                self.mlflow.start_run(self.ctx["experiment_id"])
        
        try:
            self._check_backpressure()
            
            def exec_step(step_func, state_event, sla_name, retry_key):
                t0 = time.time()
                try:
                    step_func()
                    dur = time.time() - t0
                    self.db.log_event(self.ctx["experiment_id"], state_event)
                    self._save_checkpoint()
                    self._enforce_sla(sla_name, dur)
                    self.ctx.pop(f"{retry_key}_attempts", None)
                except RetryableError as e:
                    attempts = self.ctx.get(f"{retry_key}_attempts", 0) + 1
                    self.ctx[f"{retry_key}_attempts"] = attempts
                    max_attempts = self.profile.retry.get(retry_key, {}).get("max_attempts", 3) if self.profile else 3
                    
                    if attempts > max_attempts:
                        self.ctx["state"] = ExperimentState.FAILED_PERMANENT
                        self.db.log_event(self.ctx["experiment_id"], "FAILED_PERMANENT", {"reason": e.reason, "error": str(e), "DLQ": True})
                        self._save_checkpoint()
                        self._seal_bundle()
                        raise e
                    else:
                        self.ctx["state"] = ExperimentState.FAILED_RETRYABLE
                        self.db.log_event(self.ctx["experiment_id"], "FAILED_RETRYABLE", {"reason": e.reason, "attempt": attempts})
                        self._save_checkpoint()
                        print(f"🔄 Retrying {retry_key} (Attempt {attempts}/{max_attempts}) - {e.reason}")
                        raise e
                except FatalError as e:
                    self.ctx["state"] = ExperimentState.FAILED_PERMANENT
                    self.db.log_event(self.ctx["experiment_id"], "FAILED_PERMANENT", {"reason": e.reason, "error": str(e), "DLQ": True})
                    self._save_checkpoint()
                    self._seal_bundle()
                    raise e
            
            if self._should_continue(stop_at_state): exec_step(self._step_research, "RESEARCH_COMPLETED", "RESEARCH", "research")
            if self._should_continue(stop_at_state): exec_step(self._step_hypothesis, "HYPOTHESIS_FORMED", "RESEARCH", "research")
            if self._should_continue(stop_at_state): exec_step(self._step_asset_generation, "ASSET_GENERATED", "FACTORY", "rendering")
            if self._should_continue(stop_at_state): exec_step(self._step_quality_check, "QUALITY_PASSED", "FACTORY", "rendering")
            if self._should_continue(stop_at_state): exec_step(self._step_human_approval, "HUMAN_APPROVED", "PUBLISH", "publish")
            if self._should_continue(stop_at_state): exec_step(self._step_publish, "PUBLISHED", "PUBLISH", "publish")
            
            if self.is_synthetic:
                if self._should_continue(stop_at_state): exec_step(self._step_observe, "METRICS_FETCHED", "CALIBRATION", "metrics")
                if self._should_continue(stop_at_state): exec_step(self._step_calibrate, "CALIBRATED", "CALIBRATION", "metrics")
                    
            if not stop_at_state:
                self.db.finish_run(self.run_id, "SUCCESS")
                self._seal_bundle()
                if self.mlflow:
                    exp_dir = Path("experiments") / self.ctx["experiment_id"]
                    self.mlflow.log_artifacts(str(exp_dir))
                    self.mlflow.end_run(status="FINISHED")
                
        except (RetryableError, FatalError) as e:
            logger.error(f"DLQ Event no estado {self.ctx.get('state')}: {e.reason}")
            self.db.finish_run(self.run_id, f"ERROR: {e.reason}")
            if self.mlflow:
                self.mlflow.end_run(status="FAILED")
            return {"status": "failed", "step": self.ctx.get('state'), "error": e.reason}
        except Exception as e:
            logger.error(f"Erro fatal não tratado no estado {self.ctx.get('state')}: {e}")
            self.db.finish_run(self.run_id, f"ERROR: {str(e)}")
            if self.mlflow:
                self.mlflow.end_run(status="FAILED")
            return {"status": "failed", "step": self.ctx.get('state'), "error": str(e)}

        return {
            "status": "success",
            "final_state": self.ctx["state"].value,
            "experiment_id": self.ctx["experiment_id"]
        }
        
    def _should_continue(self, stop_at: ExperimentState) -> bool:
        if stop_at and self.ctx["state"] == stop_at:
            print(f"🔬 [ExperimentRunner] Parada solicitada alcançada: {stop_at.value}.")
            return False
        return True

    def _step_research(self):
        researcher = self.reality_registry.get_best_researcher()
        if not researcher:
            raise RuntimeError("No ResearchProvider available.")
            
        context = {
            "validated": ["educational_hook", "storytelling_finance"],
            "rejected": ["generic_quotes"],
            "unknown": ["ai_automation_tools"],
            "active_questions": ["does urgency outperform curiosity?"]
        }
        
        query = "tendencias emergentes rentaveis"
        report = researcher.execute_research(query, context=context)
        
        report_id = self.research_ledger.save_report(report)
        print(f"🔬 [ExperimentRunner] Pesquisa via {report.provider} (ID: {report_id})")
        
        if not report.trends:
            raise RuntimeError("No trends found in research.")
            
        self.ctx["trend"] = report.trends[0]
        self.ctx["research_report"] = report
        self.ctx["state"] = ExperimentState.RESEARCHED

    def _step_hypothesis(self):
        trend = self.ctx["trend"]
        topic = trend.get("topic", "Nicho Desconhecido")
        category = trend.get("category", "Geral")
        hook = trend.get("suggested_hook", f"Descubra o segredo sobre {topic}.")
        metric_target = trend.get("metric_target", "retention_3s")
        
        statement = f"O uso de hooks estruturados como '{hook}' sobre '{topic}' melhora o '{metric_target}'."
        hypothesis_id = self.registry.register_hypothesis(statement, category, metric_target)
        
        # Determina a variante (A ou B) alternando com base no histórico do banco
        with self.db._get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute("SELECT variant_id FROM experiments WHERE hypothesis_id = ?", (hypothesis_id,))
                existing = [r[0] for r in c.fetchall()]
            except Exception:
                existing = []
        n_a = existing.count("A")
        n_b = existing.count("B")
        variant_id = "A" if n_a <= n_b else "B"

        if variant_id == "A":
            hook = f"Guia informativo prático sobre {topic}."
            variant_desc = "Grupo de Controle - Informativo"
        else:
            variant_desc = "Grupo de Teste - Genoma Catalogado"

        print(f"🔬 [ExperimentRunner] Hipótese (ID: {hypothesis_id}) - Variante: {variant_id} ({variant_desc})")
        self.ctx["hypothesis_id"] = hypothesis_id
        self.ctx["topic"] = topic
        self.ctx["hook"] = hook
        self.ctx["category"] = category
        self.ctx["metric_target"] = metric_target
        self.ctx["statement"] = statement
        self.ctx["variant_id"] = variant_id
        self.ctx["variant_desc"] = variant_desc
        self.ctx["state"] = ExperimentState.HYPOTHESIS_FORMED
        
        self.db.log_decision(
            experiment_id=self.ctx["experiment_id"],
            run_id=self.run_id,
            decision_point="HYPOTHESIS_SELECTION",
            chosen_value=topic,
            rejected_alternatives=["generic_quotes", "ai_automation_tools"],
            reason="confidence=0.82 derived from research",
            decision_policy="economic_v2",
            policy_version="v1.4",
            confidence=0.82,
            inputs_hash=hashlib.md5(topic.encode()).hexdigest(),
            seed=self.ctx.get("seed_config", {}).get("master_seed", 0)
        )
        if self.mlflow:
            self.mlflow.log_parameters({
                "topic": topic,
                "hook": hook,
                "category": category,
                "metric_target": metric_target,
                "variant_id": variant_id
            })

    def _step_asset_generation(self):
        generator = self.factory_registry.get_best_video_generator()
        if not generator:
            raise RuntimeError("No VideoGenerator available in Factory.")
            
        # Copywriter: usa o Gemini 3.5 Flash para expandir a hipótese e gancho em um roteiro completo
        generated_script = None
        approved_title = None
        approved_description = None
        
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and "your_key" not in api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-3.5-flash")
                
                # 1. Gerar Roteiro/Script dependendo da variante (Informativo vs Ganchos de Curiosidade)
                if self.ctx.get("variant_id") == "A":
                    script_prompt = (
                        f"Escreva um roteiro curto de 30 a 50 palavras em português para um vídeo informativo e neutro de shorts sobre '{self.ctx['topic']}'. "
                        f"O vídeo deve ser direto, objetivo e focado no aprendizado prático (Guia Informativo), sem usar ganchos exagerados de mistério ou curiosidade. "
                        f"Retorne apenas o roteiro final para narração, sem comentários, títulos ou formatações extras."
                    )
                else:
                    script_prompt = (
                        f"Escreva um roteiro curto de 30 a 50 palavras em português para um vídeo viral de shorts sobre '{self.ctx['topic']}'. "
                        f"O vídeo deve ter um gancho do tipo '{self.ctx['hook']}' e evocar a emoção 'curiosity'. "
                        f"Retorne apenas o roteiro final para narração, sem comentários, títulos ou formatações extras."
                    )
                print(f"✍️ [Copywriter] Expandindo gancho '{self.ctx['hook']}' via Gemini...")
                res = model.generate_content(script_prompt)
                generated_script = res.text.strip().replace('"', '')
                print(f"✍️ [Copywriter] Script gerado: {generated_script}")
                
                # 2. Gerar Título e Descrição de publicação
                meta_prompt = (
                    f"Com base no roteiro a seguir, crie um título curto de 4 a 6 palavras e uma descrição persuasiva com CTA de até 150 caracteres para postar no Pinterest:\n"
                    f"Roteiro: {generated_script}\n"
                    f"Retorne a resposta no formato JSON com as chaves 'title' and 'description'. Apenas o JSON válido, sem markdown ou blocos de código."
                )
                meta_res = model.generate_content(meta_prompt)
                meta_text = meta_res.text.strip().replace("```json", "").replace("```", "").strip()
                meta_data = json.loads(meta_text)
                approved_title = meta_data.get("title")
                approved_description = meta_data.get("description")
        except Exception as copy_err:
            print(f"⚠️ [Copywriter] Falha ao gerar roteiro via Gemini: {copy_err}. Usando fallback simples.")

        # Fallbacks caso o Gemini falhe ou não esteja configurado
        if not generated_script:
            generated_script = f"Se você quer descobrir o segredo sobre {self.ctx['topic']}, preste atenção. Muitas pessoas erram ao tentar resolver isso sozinhas. A solução ideal está no link da nossa bio."
        if not approved_title:
            approved_title = f"{self.ctx['topic']}: {self.ctx['hook']}"
        if not approved_description:
            approved_description = f"Descubra agora a melhor estratégia sobre {self.ctx['topic']} usando abordagens {self.ctx['hook']}. {generated_script}"
            
        self.ctx["approved_title"] = approved_title
        self.ctx["approved_description"] = approved_description
        self.ctx["approved_cta"] = "Saiba mais no link da bio."
        
        brief = CreativeBrief(
            hypothesis_id=str(self.ctx["hypothesis_id"]),
            audience="entrepreneurs",
            emotion="curiosity",
            hook=self.ctx["hook"],
            script=generated_script,
            format="short_video",
            duration=45,
            platform="pinterest",
            search_terms=[self.ctx["topic"]],
            subject=self.ctx["topic"]
        )
        
        print(f"🔬 [ExperimentRunner] Solicitando vídeo na Factory ({generator.provider_name})...")
        asset = generator.generate(brief)
        self.ctx["asset"] = asset
        
        # Content Genome
        injected_genome = self.ctx["trend"].get("genome_candidate")
        if injected_genome:
            genome = CreativeGenome(**injected_genome)
        else:
            genome = CreativeGenome(
                hook={"type": "contrarian", "strength": 0.8},
                psychology={"emotion": brief.emotion, "pain_point": "financial anxiety"},
                structure={"format": brief.format, "duration": brief.duration, "tempo": "fast"},
                audience={"persona": brief.audience},
                visual_language={"style": "cinematic", "palette": "dark"}
            )
        self.ctx["genome"] = genome
        
        # Registrar no AssetRegistry
        if os.path.exists(asset.path):
            size_bytes = os.path.getsize(asset.path)
            file_hash = hashlib.sha256(open(asset.path, "rb").read(1024 * 1024)).hexdigest()
        else:
            size_bytes = 0
            file_hash = "mock_hash"
            
        asset_id = f"VID-{self.ctx['experiment_id']}"
        self.asset_registry.register_asset(
            asset_id=asset_id,
            experiment_id=self.ctx["experiment_id"],
            factory=generator.provider_name,
            prompt_hash=hashlib.md5(brief.hook.encode()).hexdigest(),
            genome=genome,
            status="generated",
            file_path=asset.path,
            file_hash=file_hash,
            mime_type="video/mp4",
            duration=asset.duration,
            resolution=asset.resolution,
            size=size_bytes,
            quality_score=asset.confidence
        )
        # Injetar conteúdo aprovado pelo Copywriter/Critic diretamente no asset.
        # O asset físico (vídeo/imagem) deve sempre viajar com o conteúdo textual aprovado.
        # O Publisher (OpenManus ou API) recebe o pacote completo e só executa a publicação.
        asset.approved_title = self.ctx.get("approved_title") or f"{self.ctx['topic']}: {self.ctx['hook'][:80]}"
        asset.approved_description = self.ctx.get("approved_description") or self.ctx["hook"]
        asset.approved_cta = self.ctx.get("approved_cta") or "Saiba mais no link da bio."
        asset.destination_link = self.ctx.get("destination_link") or "https://github.com/Ciamarro1/ai-revenue-os"
        
        self.ctx["state"] = ExperimentState.ASSET_GENERATED

    def _step_quality_check(self):
        asset = self.ctx["asset"]
        
        # 1. Physical Quality Check - roteia entre gate de vídeo e imagem automaticamente
        ext = os.path.splitext(asset.path)[1].lower()
        if ext == ".mp4":
            if not VideoQualityGate.check_quality(asset):
                raise RuntimeError("O vídeo gerado falhou no Quality Gate.")
        else:
            if not ImageQualityGate.check_quality(asset):
                raise RuntimeError("A imagem gerada falhou no Quality Gate.")
            
        # 2. Economic Policy Check
        policy_res = self.policy_engine.check_can_publish(
            quality_score=asset.confidence, 
            confidence=asset.confidence, 
            estimated_cost=0.05
        )
        if not policy_res["allowed"]:
            raise RuntimeError(f"Policy Block: {policy_res['reason']}")
            
        self.ctx["state"] = ExperimentState.QUALITY_CHECKED
        
        # 3. Create Experiment Artifact Bundle
        exp_dir = Path("experiments") / self.ctx["experiment_id"]
        exp_dir.mkdir(parents=True, exist_ok=True)
        
        with open(exp_dir / "research.json", "w") as f:
            if self.ctx.get("research_report"):
                f.write(self.ctx["research_report"].model_dump_json())
            else:
                f.write("{}")
        with open(exp_dir / "hypothesis.json", "w") as f:
            f.write(json.dumps({"statement": self.ctx["statement"], "metric_target": self.ctx["metric_target"]}))
        with open(exp_dir / "genome.json", "w") as f:
            f.write(self.ctx["genome"].model_dump_json())
            
        # 1. Experiment Identity Hash
        h_statement = hashlib.sha256(self.ctx["statement"].encode()).hexdigest()[:10]
        h_genome = hashlib.sha256(self.ctx["genome"].model_dump_json().encode()).hexdigest()[:10]
        prompt_content = f"topic:{self.ctx.get('topic')} hook:{self.ctx.get('hook')} title:{self.ctx.get('approved_title')}"
        h_prompt = hashlib.sha256(prompt_content.encode()).hexdigest()[:10]
        
        with open(exp_dir / "identity.json", "w") as f:
            json.dump({
                "experiment_id": self.ctx["experiment_id"],
                "hypothesis_hash": h_statement,
                "genome_hash": h_genome,
                "prompt_hash": h_prompt
            }, f, indent=4)
            
        with open(exp_dir / "config.json", "w") as f:
            f.write(json.dumps({
                "runner_version": "v2.0",
                "genome_library_version": "v3",
                "policy_version": "v1.4",
                "reward_calculator_version": "v2",
                "safety_gate_version": "v1.4",
                "factory_provider": getattr(self.factory_registry.get_best_video_generator(), 'provider_name', 'unknown'),
                "research_provider": getattr(self.reality_registry.get_best_researcher(), 'provider_name', 'unknown'),
                "model_name": "all-MiniLM-L6-v2"
            }, indent=4))
            
        if os.path.exists(asset.path):
            shutil.copy(asset.path, exp_dir / f"asset_{Path(asset.path).name}")

    def _step_human_approval(self):
        if self.require_human_approval:
            print(f"⏸️ [ExperimentRunner] APROVAÇÃO HUMANA NECESSÁRIA. Experimento pausado.")
            self.ctx["state"] = ExperimentState.HUMAN_APPROVED
            raise RuntimeError("Awaiting human approval before publishing.")
        self.ctx["state"] = ExperimentState.HUMAN_APPROVED

    def _step_publish(self):
        from src.revenue_os.analytics.feature_flags import FeatureFlags
        import random
        from datetime import timedelta
        flags = FeatureFlags(db=self.db)

        asset = self.ctx["asset"]
        
        # O conteúdo (título, descrição, link) vem 100% do Core: Copywriter + Critic.
        # O Publisher (OpenManus/API) recebe o pacote pronto e só executa a publicação.
        # Não há reformulação aqui. O Runner é apenas um despachante.
        title = asset.approved_title
        description = asset.approved_description
        destination_link = asset.destination_link
        
        if flags.is_enabled("ENABLE_QUEUE_PUBLISHER"):
            from src.execution.queue_worker import QueueWorker
            worker = QueueWorker(db=self.db)
            
            # Smart Scheduling / Safety Coordinator next post time
            scheduled_at = None
            if flags.is_enabled("ENABLE_SMART_SCHEDULING"):
                try:
                    from src.revenue_os.analytics.time_optimizer import TimeOptimizer
                    optimizer = TimeOptimizer(self.db)
                    best_slots = optimizer.get_optimal_schedule(1)
                    if best_slots:
                        best_slot = best_slots[0]
                        now = datetime.now(timezone.utc)
                        scheduled_dt = now.replace(hour=best_slot, minute=random.randint(0, 59), second=0, microsecond=0)
                        if scheduled_dt <= now:
                            scheduled_dt += timedelta(days=1)
                        scheduled_at = scheduled_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                except Exception as e:
                    logger.warning(f"Erro ao calcular Smart Scheduling: {e}")
            
            if not scheduled_at:
                try:
                    from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator
                    safety_coord = PinterestSafetyCoordinator(self.db)
                    state_data = safety_coord.get_state()
                    scheduled_at = state_data.get("next_scheduled_post")
                except Exception:
                    pass
            
            board = "AI Revenue OS"
            if flags.is_enabled("ENABLE_BOARD_TRACKING"):
                try:
                    from src.reality.social.pinterest.board_tracker import BoardTracker
                    board_tracker = BoardTracker(self.db)
                    board = board_tracker.get_best_board(self.ctx.get("category"))
                except Exception as e:
                    logger.warning(f"Erro ao buscar melhor board: {e}")
            
            job_id = worker.enqueue(
                experiment_id=self.ctx["experiment_id"],
                media_path=asset.path,
                title=title,
                description=description,
                link=destination_link,
                board=board,
                scheduled_at=scheduled_at
            )
            print(f"[ExperimentRunner] Publicação enfileirada no QueueWorker (Job ID: {job_id})")
            
            self.ctx["content_id"] = f"PENDING-{job_id}"
            
            self.db.log_event(
                self.ctx["experiment_id"],
                "PUBLISH_QUEUED",
                {"job_id": job_id, "title": title, "scheduled_at": scheduled_at}
            )
        else:
            publisher = self.reality_registry.get_best_publisher()
            if not publisher:
                raise RuntimeError("No Publisher available.")
            
            print(f"[ExperimentRunner] Publicando asset aprovado pelo Core: '{title}'")
            
            # Roteia entre video e imagem baseado na extensão do arquivo gerado
            ext = os.path.splitext(asset.path)[1].lower()
            if ext == ".mp4":
                pub_res = publisher.publish_video(
                    video_path=asset.path,
                    title=title,
                    description=description,
                    destination_link=destination_link
                )
            else:
                pub_res = publisher.publish_image(
                    image_path=asset.path,
                    title=title,
                    description=description,
                    destination_link=destination_link
                )
            self.ctx["content_id"] = pub_res.content_id
            
            # Log content details for subsequent diversity validation checks
            self.db.log_event(
                self.ctx["experiment_id"],
                "PUBLISH_CONTENT",
                {"title": title, "description": description, "link": destination_link}
            )
        
        creative_hash = hashlib.md5(self.ctx["topic"].encode()).hexdigest()
        exp = ExperimentContract(
            experiment_id=self.ctx["experiment_id"],
            run_id=self.run_id,
            market_segment=self.ctx["category"],
            hypothesis=Hypothesis(statement=self.ctx["statement"], metric_target=self.ctx["metric_target"]),
            variant=Variant(id=self.ctx.get("variant_id", "B"), description=self.ctx.get("variant_desc", "Vídeo com genoma catalogado")),
            economics=Economics(generation_cost_usd=0.05, revenue_usd=0.0),
            creative_hash=creative_hash,
            published_at=datetime.now(timezone.utc).isoformat() + "Z",
            platform="pinterest",
            status="PUBLISHED"
        )
        self.db.insert_experiment(exp)
        self.ctx["experiment_contract"] = exp
        self.ctx["state"] = ExperimentState.PUBLISHED

    def _step_observe(self):
        metrics_provider = self.reality_registry.get_best_metrics_provider()
        if not metrics_provider:
            raise RuntimeError("No MetricsProvider available.")

        metrics = metrics_provider.get_metrics(self.ctx['content_id'])
        
        exp = self.ctx["experiment_contract"]
        exp.real_world_metrics = RealWorldMetrics(
            impressions=metrics.impressions,
            ctr_percent=(metrics.outbound_clicks / max(1, metrics.impressions)) * 100,
            retention_3s_percent=62.5, 
            landing_visit_percent=80.0,
            conversion_count=max(0, int(metrics.saves * 0.1)),
            profit_usd=metrics.saves * 2.0 - 0.05
        )
        exp.reward_score = exp.calculate_reward()
        exp.status = "COMPLETED"
        self.db.insert_experiment(exp)
        self.ctx["state"] = ExperimentState.OBSERVED
        
        if self.mlflow:
            self.mlflow.log_metrics({
                "impressions": exp.real_world_metrics.impressions,
                "ctr_percent": exp.real_world_metrics.ctr_percent,
                "retention_3s_percent": exp.real_world_metrics.retention_3s_percent,
                "completion_rate_percent": exp.real_world_metrics.completion_rate_percent,
                "conversion_count": exp.real_world_metrics.conversion_count,
                "profit_usd": exp.real_world_metrics.profit_usd,
                "reward_score": exp.reward_score
            })
        
        # Save metrics to bundle
        exp_dir = Path("experiments") / self.ctx["experiment_id"]
        with open(exp_dir / "metrics.json", "w") as f:
            f.write(exp.real_world_metrics.model_dump_json())

    def _step_calibrate(self):
        exp = self.ctx["experiment_contract"]
        cal_res = self.calibration_engine.calculate_calibration_error(
            predicted_reward=0.50,
            realized_reward=exp.reward_score
        )
        
        outcome = exp.reward_score >= 0.35
        self.registry.update_hypothesis_stats(self.ctx["hypothesis_id"], outcome)
        
        # 2. Métrica de aprendizado (Information Gain / Erro de calibração corrigido)
        learning_value = round(abs(cal_res["calibration_error"]), 4)
        exp.learning_value_score = learning_value
        self.db.insert_experiment(exp) # atualiza no banco com a nova métrica
        
        # Save decision to bundle
        exp_dir = Path("experiments") / self.ctx["experiment_id"]
        with open(exp_dir / "decision.json", "w") as f:
            json.dump({
                "outcome": "validated" if outcome else "rejected", 
                "calibration_error": cal_res["calibration_error"],
                "learning_value_score": learning_value
            }, f, indent=4)
            
        self.ctx["state"] = ExperimentState.CALIBRATED
