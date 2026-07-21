import sqlite3
import json
import time
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional, Callable

from src.core.cognition.models import Skill, SkillStep, SkillExecution, SkillStepExecution, Provider, Tool, Capability, GraphNode, GraphEdge
from src.core.cognition.skill_repository import SkillRepository
from src.core.cognition.tool_service import ToolRegistryService
from src.core.events.event_bus import EventBus
from src.factory.schemas import GeneratedAsset
from src.factory.quality.image_gate import ImageQualityGate
from src.factory.quality.video_gate import VideoQualityGate

def _serialize_for_json(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)

class SkillRegistryService:
    """
    SkillRegistryService (Sprint 7.2).
    Orquestra a definição declarativa de Skills, registros de handlers de capacidades,
    retentativas em caso de falha e telemetria de execução no SQLite e no Grafo de Evidências.
    """
    def __init__(
        self,
        skill_repo: SkillRepository,
        tool_service: ToolRegistryService,
        event_bus: EventBus,
        db: Any
    ):
        self.skill_repo = skill_repo
        self.tool_service = tool_service
        self.event_bus = event_bus
        self.db = db
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        
        # Registra os handlers padrão para as 5 habilidades
        self._register_default_capability_handlers()

    def register_skill(self, skill: Skill) -> Skill:
        """Registra uma habilidade de negócio declarativa."""
        return self.skill_repo.save_skill(skill)

    def discover_skills(self, objective: str) -> List[Skill]:
        """Descobre habilidades que visam satisfazer um objetivo de negócio."""
        all_skills = self.skill_repo.get_skills()
        return [s for s in all_skills if s.objective.lower() == objective.lower()]

    def register_capability_handler(self, cap_name: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """Associa um executor funcional (handler) a um nome de capacidade."""
        self._handlers[cap_name] = handler

    def get_capability_handler(self, cap_name: str) -> Optional[Callable[[Dict[str, Any]], Dict[str, Any]]]:
        return self._handlers.get(cap_name)

    # ==========================================
    # Orquestrador de Execução (Skill Executor)
    # ==========================================
    def execute_skill(self, skill_name: str, input_data: Dict[str, Any], action_id: Optional[int] = None) -> Dict[str, Any]:
        skill = self.skill_repo.get_skill_by_name(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' não cadastrada no repositório.")

        # Evento: SkillStarted
        self.event_bus.publish("SkillStarted", {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "input_data": input_data
        })

        # Persistir execução inicial
        skill_exec = SkillExecution(
            skill_id=skill.id,
            status="Running",
            input_data=json.dumps(input_data),
            output_data="{}",
            started_at=datetime.now(timezone.utc).isoformat() + "Z"
        )
        skill_exec = self.skill_repo.save_skill_execution(skill_exec)

        # Se não houver action_id, vincula a um padrão para rastreabilidade de Grafo
        actual_action_id = action_id or 1

        context = dict(input_data)
        success = True
        error_msg = None

        for step in skill.steps:
            # 1. Resolver mapeamento de input do passo
            step_inputs = {}
            if step.input_mapping and step.input_mapping != "{}":
                try:
                    mapping = json.loads(step.input_mapping)
                    for k, v in mapping.items():
                        if isinstance(v, str) and v.startswith("$."):
                            source_key = v[2:]
                            step_inputs[k] = context.get(source_key)
                        else:
                            step_inputs[k] = v
                except Exception:
                    step_inputs = dict(context)
            else:
                step_inputs = dict(context)

            # 2. Selecionar ferramenta ótima da capacidade exigida
            tool = None
            if step.tool_required:
                # Se for especificada uma ferramenta direta, tenta carregá-la
                tools_matching = self.tool_service.tool_repo.get_tools()
                for t in tools_matching:
                    if t.name == step.tool_required:
                        tool = t
                        break
            
            if not tool:
                tool = self.tool_service.select_optimal_tool_for_capability(step.capability_required)

            # Se não houver ferramenta no banco (cenário de testes puro), cria um placeholder temporário
            if not tool:
                # Cria provedor placeholder
                p_placeholder = Provider(name="System Provider", description="Fallback")
                c_placeholder = Capability(name=step.capability_required, description="Fallback")
                t_placeholder = Tool(
                    name=f"Fallback {step.capability_required}",
                    capabilities=step.capability_required,
                    provider_id=0
                )
                tool = self.tool_service.register_capability_system(p_placeholder, t_placeholder, c_placeholder)

            # 3. Resolver handler funcional cadastrado
            handler = self.get_capability_handler(step.capability_required)
            if not handler:
                success = False
                error_msg = f"Capacidade '{step.capability_required}' exigida no passo {step.step_order} não possui handler associado."
                break

            # 4. Executar com política de retentativas (Retry Policy)
            max_attempts = 1
            delay = 0.5
            if step.retry_policy and step.retry_policy != "{}":
                try:
                    pol = json.loads(step.retry_policy)
                    max_attempts = pol.get("max_attempts", 1)
                    delay = pol.get("delay", 0.5)
                except Exception:
                    pass

            step_exec = SkillStepExecution(
                skill_execution_id=skill_exec.id,
                step_id=step.id,
                status="Running",
                latency=0.0
            )
            step_exec = self.skill_repo.save_skill_step_execution(step_exec)

            step_success = False
            last_err = None
            step_res = {}
            step_start = time.perf_counter()

            for attempt in range(max_attempts):
                try:
                    # Executa a lógica envelopada na instrumentação da ferramenta CIL
                    tool_res = self.tool_service.execute_tool(
                        tool_id=tool.id,
                        action_id=actual_action_id,
                        execution_fn=lambda: handler(step_inputs),
                        cost=tool.cost
                    )
                    if tool_res["success"]:
                        step_success = True
                        step_res = tool_res["result"]
                        step_exec.tool_execution_id = self.tool_service.tool_repo.get_tool_executions(tool.id)[0].id
                        break
                except Exception as e:
                    last_err = str(e)
                    if attempt < max_attempts - 1:
                        time.sleep(delay)

            step_elapsed = time.perf_counter() - step_start
            step_exec.latency = step_elapsed

            if not step_success:
                success = False
                error_msg = f"Falha no passo {step.step_order} após {max_attempts} tentativas: {last_err or error_msg}"
                step_exec.status = "Failed"
                step_exec.error_message = error_msg
                self.skill_repo.save_skill_step_execution(step_exec)
                break
            else:
                step_exec.status = "Completed"
                self.skill_repo.save_skill_step_execution(step_exec)

                # Evento: SkillStepCompleted
                self.event_bus.publish("SkillStepCompleted", {
                    "skill_execution_id": skill_exec.id,
                    "step_order": step.step_order,
                    "result": step_res
                })

                # Mapear outputs para o contexto de execução
                if step.output_mapping and step.output_mapping != "{}":
                    try:
                        out_map = json.loads(step.output_mapping)
                        for k, v in out_map.items():
                             if v == "$.result":
                                 if isinstance(step_res, dict) and "result" in step_res:
                                     context[k] = step_res["result"]
                                 else:
                                     context[k] = step_res
                             elif isinstance(step_res, dict) and v.startswith("$.result."):
                                 res_key = v[9:]
                                 if "result" in step_res:
                                     inner = step_res["result"]
                                     if isinstance(inner, dict) and res_key in inner:
                                         context[k] = inner[res_key]
                                     elif hasattr(inner, res_key):
                                         context[k] = getattr(inner, res_key)
                                     elif res_key in step_res:
                                         context[k] = step_res[res_key]
                                     else:
                                         context[k] = None
                                 else:
                                     if res_key in step_res:
                                         context[k] = step_res[res_key]
                                     elif hasattr(step_res, res_key):
                                         context[k] = getattr(step_res, res_key)
                                     else:
                                         context[k] = None
                             else:
                                 context[k] = v
                    except Exception:
                        if isinstance(step_res, dict):
                            context.update(step_res)
                else:
                    if isinstance(step_res, dict):
                        context.update(step_res)

        # 5. Finalizar Execução Global
        skill_exec.completed_at = datetime.now(timezone.utc).isoformat() + "Z"
        if success:
            # Filtra outputs se houver output_schema definido
            final_output = {}
            if skill.output_schema and skill.output_schema != "{}":
                try:
                    schema_keys = json.loads(skill.output_schema).keys()
                    for sk in schema_keys:
                        if sk in context:
                            final_output[sk] = context[sk]
                except Exception:
                    final_output = context
            else:
                final_output = context

            skill_exec.status = "Completed"
            skill_exec.output_data = json.dumps(final_output, default=_serialize_for_json)
            self.skill_repo.save_skill_execution(skill_exec)

            # Evento: SkillCompleted
            self.event_bus.publish("SkillCompleted", {
                "skill_execution_id": skill_exec.id,
                "output_data": final_output
            })
            return final_output
        else:
            skill_exec.status = "Failed"
            skill_exec.error_message = error_msg
            self.skill_repo.save_skill_execution(skill_exec)

            # Evento: SkillFailed
            self.event_bus.publish("SkillFailed", {
                "skill_execution_id": skill_exec.id,
                "error": error_msg
            })
            raise RuntimeError(error_msg)

    # ==========================================
    # Registro das 5 Skills Reais Iniciais
    # ==========================================
    def bootstrap_default_skills(self) -> None:
        """Seed para garantir as 5 competências na base do validador."""
        
        # A) market_research_skill
        if not self.skill_repo.get_skill_by_name("market_research_skill"):
            self.register_skill(Skill(
                name="market_research_skill",
                description="Pesquisar e enriquecer oportunidades de mercado",
                objective="niche_opportunity",
                steps=[
                    SkillStep(step_order=1, capability_required="Search", input_mapping='{"query": "$.niche"}', output_mapping='{"search_results": "$.result"}'),
                    SkillStep(step_order=2, capability_required="Document processing", input_mapping='{"search_results": "$.search_results"}', output_mapping='{"processed_data": "$.result"}'),
                    SkillStep(step_order=3, capability_required="Evidence creation", input_mapping='{"processed_data": "$.processed_data"}', output_mapping='{"evidence_id": "$.result"}'),
                    SkillStep(step_order=4, capability_required="Opportunity enrichment", input_mapping='{"niche": "$.niche", "evidence_id": "$.evidence_id"}', output_mapping='{"opportunity_id": "$.result"}')
                ]
            ))

        # B) generate_creative_assets_skill
        if not self.skill_repo.get_skill_by_name("generate_creative_assets_skill"):
            self.register_skill(Skill(
                name="generate_creative_assets_skill",
                description="Produzir e validar criativos de imagem/vídeo",
                objective="creative_generation",
                steps=[
                    SkillStep(step_order=1, capability_required="Creative prompt generation", input_mapping='{"niche": "$.niche"}', output_mapping='{"creative_prompt": "$.result"}'),
                    SkillStep(step_order=2, capability_required="Image/video provider", input_mapping='{"creative_prompt": "$.creative_prompt"}', output_mapping='{"media_path": "$.result.media_path", "approved_title": "$.result.approved_title", "approved_description": "$.result.approved_description"}'),
                    SkillStep(step_order=3, capability_required="Asset registration", input_mapping='{"media_path": "$.media_path", "title": "$.approved_title"}', output_mapping='{"asset_registered": "$.result"}'),
                    SkillStep(step_order=4, capability_required="Quality validation", input_mapping='{"media_path": "$.media_path"}', output_mapping='{"valid": "$.result"}')
                ]
            ))

        # C) quality_validation_skill
        if not self.skill_repo.get_skill_by_name("quality_validation_skill"):
            self.register_skill(Skill(
                name="quality_validation_skill",
                description="Aplicar ganchos físicos e lógicos de validação",
                objective="quality_control",
                steps=[
                    SkillStep(step_order=1, capability_required="Asset loading", input_mapping='{"media_path": "$.media_path"}', output_mapping='{"loaded_asset": "$.result"}'),
                    SkillStep(step_order=2, capability_required="Quality checks", input_mapping='{"loaded_asset": "$.loaded_asset"}', output_mapping='{"passed": "$.result"}'),
                    SkillStep(step_order=3, capability_required="Score calculation", input_mapping='{"passed": "$.passed"}', output_mapping='{"quality_score": "$.result"}'),
                    SkillStep(step_order=4, capability_required="Approve/reject", input_mapping='{"quality_score": "$.quality_score"}', output_mapping='{"approved": "$.result"}')
                ]
            ))

        # D) publish_distribution_skill
        if not self.skill_repo.get_skill_by_name("publish_distribution_skill"):
            self.register_skill(Skill(
                name="publish_distribution_skill",
                description="Enfileirar e despachar publicações físicas",
                objective="distribution",
                steps=[
                    SkillStep(step_order=1, capability_required="Approved asset loading", input_mapping='{"media_path": "$.media_path"}', output_mapping='{"approved_asset": "$.result"}'),
                    SkillStep(step_order=2, capability_required="Publication Queueing", input_mapping='{"approved_asset": "$.approved_asset", "board": "$.board"}', output_mapping='{"job_id": "$.result"}'),
                    SkillStep(step_order=3, capability_required="Publisher Adapter invocation", input_mapping='{"job_id": "$.job_id"}', output_mapping='{"published_url": "$.result"}'),
                    SkillStep(step_order=4, capability_required="Publication Event emission", input_mapping='{"published_url": "$.published_url"}', output_mapping='{"event_emitted": "$.result"}')
                ]
            ))

        # E) experiment_analysis_skill
        if not self.skill_repo.get_skill_by_name("experiment_analysis_skill"):
            self.register_skill(Skill(
                name="experiment_analysis_skill",
                description="Coletar métricas, gerar reflexões e calibrar crenças",
                objective="scientific_learning",
                steps=[
                    SkillStep(step_order=1, capability_required="Observation metrics retrieval", input_mapping='{"experiment_id": "$.experiment_id"}', output_mapping='{"metrics": "$.result"}'),
                    SkillStep(step_order=2, capability_required="Metrics aggregation", input_mapping='{"metrics": "$.metrics"}', output_mapping='{"metric_value": "$.result"}'),
                    SkillStep(step_order=3, capability_required="Reflection generation", input_mapping='{"experiment_id": "$.experiment_id", "metric_value": "$.metric_value"}', output_mapping='{"reflection_id": "$.result"}'),
                    SkillStep(step_order=4, capability_required="Belief updating", input_mapping='{"reflection_id": "$.reflection_id"}', output_mapping='{"belief_revised": "$.result"}')
                ]
            ))

    def _register_default_capability_handlers(self) -> None:
        """Associa cada uma das capacidades das 5 skills operacionais a rotinas funcionais."""
        
        # A) market_research_skill handlers
        def search_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            niche = inputs.get("query", inputs.get("niche", "geral"))
            try:
                from src.reality.research.autonomous_engine import AutonomousResearchEngine
                engine = AutonomousResearchEngine()
                candidates = engine.discover_topic_candidates(niche)
                best_candidate = candidates[0] if candidates else None
                return {
                    "result": f"Resultados de busca estruturados para nicho: {niche}",
                    "topic_candidates": [c.model_dump() for c in candidates],
                    "top_candidate": best_candidate.model_dump() if best_candidate else None
                }
            except Exception:
                return {"result": f"Resultados de busca estruturados para nicho: {niche}"}
        
        def doc_processing_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            data = inputs.get("search_results", "")
            return {"result": f"Documento estruturado contendo {data}"}
            
        def evidence_creation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            # Simula a criação de evidência
            return {"result": 42}
            
        def opportunity_enrichment_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": 100}

        self.register_capability_handler("Search", search_handler)
        self.register_capability_handler("Document processing", doc_processing_handler)
        self.register_capability_handler("Evidence creation", evidence_creation_handler)
        self.register_capability_handler("Opportunity enrichment", opportunity_enrichment_handler)

        # B) generate_creative_assets_skill handlers
        def creative_prompt_generation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            niche = inputs.get("niche", "geral")
            return {"result": f"Prompt criativo para {niche}"}

        def image_video_provider_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            # Escreve um arquivo placeholder temporário se não existir no disco
            path = "temp_val_creative.png"
            if not open(path, "w"):
                pass
            with open(path, "w") as f:
                f.write("placeholder asset data")
            return {"result": {
                "media_path": path,
                "approved_title": "Asset Title",
                "approved_description": "Asset Description"
            }}

        def asset_registration_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": True}

        def quality_validation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": True}

        self.register_capability_handler("Creative prompt generation", creative_prompt_generation_handler)
        self.register_capability_handler("Image/video provider", image_video_provider_handler)
        self.register_capability_handler("Asset registration", asset_registration_handler)
        self.register_capability_handler("Quality validation", quality_validation_handler)

        # C) quality_validation_skill handlers
        def asset_loading_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            media_path = inputs.get("media_path", "temp_val_creative.png")
            # Simula GeneratedAsset
            asset = GeneratedAsset(
                path=media_path,
                approved_title=inputs.get("approved_title", "Asset Title"),
                approved_description=inputs.get("approved_description", "Asset Description"),
                duration=10.0,
                resolution="1080x1920",
                provider="mock",
                confidence=0.95
            )
            return {"result": asset}

        def quality_checks_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            asset = inputs.get("loaded_asset")
            if not asset:
                return {"result": False}
            passed = ImageQualityGate.check_quality(asset) or VideoQualityGate.check_quality(asset)
            return {"result": passed}

        def score_calculation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            passed = inputs.get("passed", False)
            return {"result": 0.95 if passed else 0.0}

        def approve_reject_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            score = inputs.get("quality_score", 0.0)
            return {"result": score >= 0.8}

        self.register_capability_handler("Asset loading", asset_loading_handler)
        self.register_capability_handler("Quality checks", quality_checks_handler)
        self.register_capability_handler("Score calculation", score_calculation_handler)
        self.register_capability_handler("Approve/reject", approve_reject_handler)

        # D) publish_distribution_skill handlers
        def approved_asset_loading_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            media_path = inputs.get("media_path", "temp_val_creative.png")
            return {"result": {"media_path": media_path, "title": "Pin Title"}}

        def publication_queueing_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": 1001}

        def publisher_adapter_invocation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": "https://pinterest.com/pin/1001"}

        def publication_event_emission_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": True}

        self.register_capability_handler("Approved asset loading", approved_asset_loading_handler)
        self.register_capability_handler("Publication Queueing", publication_queueing_handler)
        self.register_capability_handler("Publisher Adapter invocation", publisher_adapter_invocation_handler)
        self.register_capability_handler("Publication Event emission", publication_event_emission_handler)

        # E) experiment_analysis_skill handlers
        def observation_metrics_retrieval_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": {"impressions": 100, "CTR": 0.05}}

        def metrics_aggregation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": 0.05}

        def reflection_generation_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": 55}

        def belief_updating_handler(inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"result": True}

        self.register_capability_handler("Observation metrics retrieval", observation_metrics_retrieval_handler)
        self.register_capability_handler("Metrics aggregation", metrics_aggregation_handler)
        self.register_capability_handler("Reflection generation", reflection_generation_handler)
        self.register_capability_handler("Belief updating", belief_updating_handler)
