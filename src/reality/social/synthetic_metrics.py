import random
from typing import Dict, Any

from src.reality.base import MetricsProvider, CanonicalMetrics

class SyntheticMetricsProvider(MetricsProvider):
    """
    Simulador de rede social ruidosa. Injeta incerteza para provar
    que o GenomeLibrary consegue extrair sinal fraco de muito ruído.
    """
    def __init__(self, hidden_regime: str = "A"):
        self.provider_name = "synthetic_simulator"
        self.confidence_score = 1.0
        self.hidden_regime = hidden_regime

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": self.provider_name}
        
    def evaluate_genome(self, attributes: Dict[str, Any]) -> CanonicalMetrics:
        """
        Retorna métricas simuladas baseadas em um padrão oculto.
        Regime A: "contrarian" + "curiosity" vence (CTR 15%). Resto (CTR 5%).
        Regime B: "educational" + "trust" vence (CTR 15%). Resto (CTR 5%).
        """
        hook = attributes.get("hook", {}).get("type", "")
        emotion = attributes.get("psychology", {}).get("emotion", "")
        
        base_ctr = 5.0
        
        if self.hidden_regime == "A":
            if hook == "contrarian" and emotion == "curiosity":
                base_ctr = 15.0
        elif self.hidden_regime == "B":
            if hook == "educational" and emotion == "trust":
                base_ctr = 15.0
                
        # Ruído aleatório (multiplicador e absoluto) simulando o mundo real
        noise_multiplier = random.uniform(0.8, 1.2)
        absolute_noise = random.uniform(-4.0, 4.0)
        
        final_ctr = max(0.1, (base_ctr * noise_multiplier) + absolute_noise)
        
        # Conversões
        base_conv_rate = final_ctr * 0.5
        final_conv_rate = max(0.0, base_conv_rate * random.uniform(0.5, 1.5))
        
        impressions = int(random.uniform(1000, 50000))
        clicks = int((final_ctr / 100.0) * impressions)
        saves = int((final_conv_rate / 100.0) * clicks)
        
        return CanonicalMetrics(
            impressions=impressions,
            outbound_clicks=clicks,
            saves=saves,
            shares=int(saves * random.uniform(0.1, 0.5)),
            retention_3s_percent=random.uniform(10.0, 60.0)
        )
        
    def get_metrics(self, content_id: str) -> CanonicalMetrics:
        # Fallback method se chamado tradicionalmente sem o genoma
        return self.evaluate_genome({})
