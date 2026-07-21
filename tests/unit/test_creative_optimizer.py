import pytest
from src.agents.creative_optimizer import CreativeOptimizerAgent

def test_creative_optimizer_pydantic_ai_shadow_mode():
    """
    Testa se o Agente consegue estruturar o Pydantic Model corretamente no modo Shadow (TestModel),
    sem consumir tokens de API reais.
    """
    agent = CreativeOptimizerAgent(use_test_model=True)
    
    brief = {"title": "Como investir em FIIs"}
    copy_data = {"hook": "Veja isso agora!"}
    critic_report = {
        "findings": [
            {"severity": "critical", "category": "retention", "message": "Vídeo muito curto."},
            {"severity": "warning", "category": "visuals", "message": "Falta dinamismo."}
        ]
    }
    
    result = agent.optimize(brief, copy_data, {}, critic_report)
    
    assert "hook" in result
    assert "search_terms" in result
    
    # O TestModel irá injetar strings padrão (como 'a' ou 'Test') de acordo com os tipos
    # O importante é que a estrutura retornou válida sem falhar no Pydantic validation
    assert isinstance(result["hook"], str)
    assert isinstance(result["search_terms"], list)
