from typing import Dict, Any

class CalibrationEngine:
    """
    O Motor de Calibração (EXP-010).
    Aferidor da falha do próprio laboratório sintético frente à Realidade.
    Objetivo: Subtrair 'Calibration Error' da Reward Final de simulações.
    """
    
    def calculate_calibration_error(self, predicted_reward: float, realized_reward: float) -> Dict[str, Any]:
        """
        Recebe a previsão teórica e o outcome real. Retorna o Delta (Erro).
        """
        # Se a diferença for negativa, o sistema é super-otimista.
        # Se for positiva, o sistema é super-pessimista.
        error_delta = abs(predicted_reward - realized_reward)
        
        # Simples heurística de alerta
        status = "ALIGNED"
        if error_delta > 0.30:
            status = "DANGEROUS_DEVIATION"
        elif error_delta > 0.15:
            status = "NEEDS_CALIBRATION"
            
        return {
            "prediction": predicted_reward,
            "reality": realized_reward,
            "calibration_error": round(error_delta, 3),
            "status": status,
            "action_required": "RECALIBRATE_SIMULATOR" if status != "ALIGNED" else "NONE"
        }
        
    def adjust_risk_factor(self, current_risk_factor: float, error_history_avg: float) -> float:
        """
        Punição Sistêmica. Se o nosso simulador vive errando (alta média de erro), 
        o Fundo aumenta o Risk Penalty global.
        """
        # Ex: Se o erro histórico é 0.20 (20% de alucinação), nós subtraímos isso da proteção atual.
        calibrated_risk = current_risk_factor * (1.0 - error_history_avg)
        return max(0.1, round(calibrated_risk, 3))
        
    def calculate_predictive_bias(self, metric_name: str, predicted: float, reality: float, context_key: str = "global") -> Dict[str, Any]:
        """
        VP-001 (Etapa 2): Aprende se o simulador superestima ou subestima a realidade
        isolando o contexto. Um viés gigantesco no nicho de 'finance' não deve
        punir a calibração perfeita do nicho de 'productivity'.
        """
        if predicted <= 0:
            return {"bias_factor": 1.0, "message": "Baseline zerada."}
            
        bias_factor = reality / predicted
        
        message = "Equilibrado"
        if bias_factor < 0.9:
            message = f"Superestimou {metric_name} em {round((1-bias_factor)*100)}% no contexto [{context_key}]."
        elif bias_factor > 1.1:
            message = f"Subestimou {metric_name} em {round((bias_factor-1)*100)}% no contexto [{context_key}]."
            
        return {
            "metric": metric_name,
            "context_key": context_key,
            "correction_multiplier": round(bias_factor + 1e-5, 2),
            "trend": message
        }
