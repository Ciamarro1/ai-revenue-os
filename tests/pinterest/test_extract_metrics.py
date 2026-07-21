import pytest
from src.reality.social.pinterest.browser import PinterestBrowserProvider

def test_mock_metrics_extraction(mock_pin_page_path):
    """
    Testa se o Playwright Scraper consegue extrair com sucesso as métricas da página mockada (Sprint P3 - Passo 3.1).
    """
    provider = PinterestBrowserProvider()
    
    # Passa o URI do arquivo local como content_id para forçar a leitura local
    mock_url = mock_pin_page_path.resolve().as_uri()
    
    metrics = provider.get_metrics(mock_url)
    
    # Valida as métricas injetadas no HTML mockado
    assert metrics.impressions == 120
    assert metrics.outbound_clicks == 15
    assert metrics.saves == 8
    assert metrics.provider == "pinterest_playwright_scraped"
