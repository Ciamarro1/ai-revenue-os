from typing import Dict, Any

class BenchmarkingEngine:
    """
    Motor de Benchmarking Semanal Interno (v5.5 LTS).
    Compara métricas operacionais da semana corrente contra semanas anteriores
    para responder se a plataforma está performando melhor do que ela mesma ao longo do tempo.
    """

    def compare_weeks(
        self,
        previous_week: Dict[str, float],
        current_week: Dict[str, float]
    ) -> Dict[str, Any]:
        
        ctr_diff = round(current_week.get("ctr", 0.0) - previous_week.get("ctr", 0.0), 4)
        roi_diff = round(current_week.get("roi", 0.0) - previous_week.get("roi", 0.0), 2)
        conversion_diff = round(current_week.get("conversion_rate", 0.0) - previous_week.get("conversion_rate", 0.0), 4)
        kqi_diff = round(current_week.get("kqi_score", 0.0) - previous_week.get("kqi_score", 0.0), 1)

        is_improving = ctr_diff >= 0 and roi_diff >= 0 and kqi_diff >= 0

        return {
            "ctr_delta": ctr_diff,
            "roi_delta": roi_diff,
            "conversion_rate_delta": conversion_diff,
            "kqi_delta": kqi_diff,
            "is_outperforming_previous_week": is_improving,
            "summary": "Desempenho semanal em evolução 🟢" if is_improving else "Degradação pontual detectada ⚠️"
        }
