import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_mock_create_pin_page_loads(mock_html_path):
    """
    Testa se o Pin Builder Mock carrega os seletores corretos do Pinterest offline.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Carrega a página mock
        mock_url = mock_html_path.resolve().as_uri()
        page.goto(mock_url)
        
        # Verifica se o input file e campos existem
        assert page.locator("input[type='file']").count() == 1
        assert page.locator("[data-testid='board-dropdown-save-button']").count() == 1
        
        context.close()
        browser.close()

def test_live_create_pin_page_loads(live_session_path):
    """
    Testa se a página real de criação de Pin carrega com a sessão live do usuário.
    """
    if not live_session_path.exists():
        pytest.skip("Ignorando teste real de criação de pin (sem sessão configurada).")
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(live_session_path))
        page = context.new_page()
        
        page.goto("https://www.pinterest.com/pin-builder/", timeout=60000)
        try:
            page.wait_for_selector("input[type='file']", timeout=20000)
            file_input_exists = True
        except Exception:
            file_input_exists = False
            
        context.close()
        browser.close()
        
        assert file_input_exists, "Input file do Pinterest não foi encontrado na página de criação real."
