import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_mock_fill_description(mock_html_path):
    """
    Testa se o Playwright consegue preencher a div contenteditable da descrição (Sprint P2 - Passo 2.4).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        mock_url = mock_html_path.resolve().as_uri()
        page.goto(mock_url)
        
        # Preenche a div de descrição
        desc_selector = "[data-testid='pin-builder-description']"
        test_desc = "Uma descrição super completa explicando cada detalhe do experimento econômico."
        
        page.wait_for_selector(desc_selector)
        page.fill(desc_selector, test_desc)
        
        # Verifica se o texto interno condiz
        filled_text = page.inner_text(desc_selector)
        assert filled_text == test_desc
        
        context.close()
        browser.close()
