import sys
import json
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import os
from pydantic_ai.models.test import TestModel

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "dummy_key_for_import"


if sys.version_info >= (3, 11):
    import tomllib
else:
    import json
    pass

# ==========================================
# Schemas de Entrada e Saída
# ==========================================
class CriticInput(BaseModel):
    tech_report: Dict[str, Any]
    video_report: Dict[str, Any]
    audio_report: Dict[str, Any]
    subtitles_report: Dict[str, Any]
    thresholds: Dict[str, Any]

class CriticFinding(BaseModel):
    severity: str = Field(description="'critical', 'warning', ou 'info'")
    category: str = Field(description="Ex: 'video', 'audio', 'retention', 'visuals', 'accessibility'")
    message: str = Field(description="Explicação da falha baseada no limiar exigido.")

class CriticEvaluation(BaseModel):
    decision: str = Field(description="'APPROVE' ou 'REJECT'")
    technical_score: int = Field(description="Nota de 0 a 100 baseada puramente na qualidade do arquivo (streams, black frames).")
    marketing_score: int = Field(description="Nota de 0 a 100 baseada na capacidade de retenção (motion, sharpness, silence).")
    overall_score: int = Field(description="Média ponderada ou nota final.")
    findings: List[CriticFinding] = Field(description="Lista detalhada de problemas encontrados.")

# ==========================================
# Inicialização do Agente PydanticAI
# ==========================================
agent = Agent(
    'google:gemini-1.5-flash',
    deps_type=CriticInput,
    output_type=CriticEvaluation,
    system_prompt=(
        "Você é o Video Critic do AI Revenue OS."
        "Seu trabalho é avaliar relatórios técnicos de vídeos (áudio, visual, legendas) contra "
        "regras e limites (thresholds) definidos pela política."
        "Você deve descontar pontos do technical_score para falhas físicas (ex: black frames, falta de stream)."
        "Você deve descontar pontos do marketing_score para UX pobre (ex: pouco dinamismo visual, silêncio inicial alto, sem legendas)."
        "Seje extremamente rígido. Vídeos sub-par destroem a retenção do laboratório."
    )
)

class VideoCriticAgent:
    """
    Video Critic Evoluído (EXP-007).
    Migrado para PydanticAI, combinando heurísticas TOML com capacidade interpretativa LLM.
    """

    def __init__(self, profile: str = "finance", use_test_model: bool = True):
        self.profile = profile
        self.thresholds = self._load_thresholds()
        self.model = TestModel() if use_test_model else None

    def _load_thresholds(self) -> Dict[str, Any]:
        config_path = Path(__file__).parent.parent / "config" / "profiles" / f"{self.profile}.toml"
        if not config_path.exists():
            return {"video": {}, "audio": {}} # fallback for testing
            
        with open(config_path, "rb") as f:
            if sys.version_info >= (3, 11):
                return tomllib.load(f)
            else:
                return {}

    def evaluate(
        self,
        report: Dict[str, Any],
        creative_meta: Dict[str, Any],
        copy_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        print(f"🔍 [VideoCritic-PydanticAI] Analisando report com base no perfil '{self.profile}'...")
        
        input_data = CriticInput(
            tech_report=report.get("technical", {}),
            video_report=report.get("video", {}),
            audio_report=report.get("audio", {}),
            subtitles_report=report.get("subtitles", {}),
            thresholds=self.thresholds
        )
        
        prompt = (
            f"Avalie o vídeo usando os seguintes dados:\n"
            f"Technical: {json.dumps(input_data.tech_report)}\n"
            f"Video: {json.dumps(input_data.video_report)}\n"
            f"Audio: {json.dumps(input_data.audio_report)}\n"
            f"Thresholds Permitidos: {json.dumps(input_data.thresholds)}"
        )
        
        print("💡 [VideoCritic] Invocando LLM via PydanticAI para julgar qualidade...")
        
        if self.model:
            result = agent.run_sync(prompt, deps=input_data, model=self.model)
        else:
            result = agent.run_sync(prompt, deps=input_data)
            
        evaluation: CriticEvaluation = result.output
        
        result_dict = {
            "decision": evaluation.decision,
            "scores": {
                "technical": evaluation.technical_score,
                "marketing": evaluation.marketing_score,
                "overall": evaluation.overall_score
            },
            "findings": [f.model_dump() for f in evaluation.findings]
        }
        
        print(f"✅ [VideoCritic] Conclusão: {evaluation.decision} (Overall: {evaluation.overall_score})")
        return result_dict
