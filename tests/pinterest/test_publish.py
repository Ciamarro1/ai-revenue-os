import pytest
from pathlib import Path
from src.execution.publisher.pinterest_playwright import PinterestPlaywrightPublisher

def test_mock_publish_cycle(mock_html_path, dummy_image):
    """
    Testa o ciclo de publicação do Playwright contra o Mock DOM offline (Sprint P2 - Passo 2.5).
    """
    publisher = PinterestPlaywrightPublisher(openrouter_key="mock_key")
    
    payload = {
        "media_path": str(dummy_image),
        "title": "Como Automatizar com Playwright",
        "description": "Guia prático de engenharia de automação.",
        "link": "https://github.com/Ciamarro1/ai-revenue-os",
        "test_url": mock_html_path.resolve().as_uri(),
        "headless": True
    }
    
    # Executa a publicação
    res = publisher.publish(payload)
    
    # Valida o resultado esperado de sucesso
    assert res["status"] == "success"
    assert "pin/12345/index.html" in res["url"]
    assert res["pin_id"] == "12345"
