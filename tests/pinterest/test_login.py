import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_login_session_file_exists(live_session_path):
    """
    Verifica se o arquivo de sessão existe (Sprint P1 - Passo 1)
    """
    if not live_session_path.exists():
        pytest.skip(
            f"Arquivo de sessão '{live_session_path}' não encontrado. "
            "Execute 'python scripts/setup_session.py --platform pinterest' para autenticar."
        )
    assert live_session_path.stat().st_size > 0

def test_login_session_is_valid(live_session_path):
    """
    Verifica se a sessão salva consegue acessar o Pinterest sem ser redirecionada para a tela de login.
    """
    if not live_session_path.exists():
        pytest.skip("Ignorando teste de validade de sessão real (sessão inexistente).")
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(live_session_path))
        page = context.new_page()
        
        # Acessa a raiz do Pinterest
        page.goto("https://www.pinterest.com/", timeout=45000)
        page.wait_for_load_state("domcontentloaded")
        
        # Se for redirecionado para /login, a sessão expirou
        current_url = page.url
        is_logged_in = "login" not in current_url
        
        context.close()
        browser.close()
        
        assert is_logged_in, f"Sessão expirou ou é inválida! Redirecionado para {current_url}."
