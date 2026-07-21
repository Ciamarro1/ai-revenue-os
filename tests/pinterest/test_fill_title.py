import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_mock_fill_title(mock_html_path):
    """
    Testa se o Playwright consegue localizar e preencher o campo de título (Sprint P2 - Passo 2.3).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        mock_url = mock_html_path.resolve().as_uri()
        page.goto(mock_url)
        
        # Preenche o título
        title_selector = "[data-testid='pin-builder-title']"
        test_title = "Como Alavancar Receita com IA"
        
        page.wait_for_selector(title_selector)
        page.fill(title_selector, test_title)
        
        # Verifica se o valor foi preenchido corretamente
        filled_value = page.input_value(title_selector)
        assert filled_value == test_title
        
        context.close()
        browser.close()
