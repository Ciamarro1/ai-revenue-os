class HealthMonitor:
    """
    O Circuit Breaker.
    Checa a sanidade das APIs externas antes do CapabilityRegistry queimar chamadas.
    """
    def __init__(self):
        # Mock de estado das APIs (Ex: Pinterest, YouTube)
        self.health_status = {
            "PinterestServer": {
                "available": True,
                "auth_valid": True,
                "rate_limit_ok": True,
                "avg_response_ms": 120
            }
        }
        
    def check_provider(self, provider_name: str) -> bool:
        """
        Retorna True se a plataforma está operacional.
        Falhas disparam circuit breaker.
        """
        if provider_name not in self.health_status:
            return False
            
        status = self.health_status[provider_name]
        return status["available"] and status["auth_valid"] and status["rate_limit_ok"]
        
    def trigger_rate_limit(self, provider_name: str):
        """Mock para estressar o sistema (Tolerância a Falhas)"""
        if provider_name in self.health_status:
            self.health_status[provider_name]["rate_limit_ok"] = False
