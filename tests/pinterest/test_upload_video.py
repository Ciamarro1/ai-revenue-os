import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_mock_upload_video(mock_html_path, dummy_video):
    """
    Testa se o Playwright consegue selecionar e definir o arquivo de vídeo no input file (Sprint P2 - Passo 2.2).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        mock_url = mock_html_path.resolve().as_uri()
        page.goto(mock_url)
        
        # Seleciona o input e faz o upload do vídeo
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(str(dummy_video))
        
        # Verifica se o arquivo foi atrelado
        files_count = page.evaluate("document.querySelector('input[type=\"file\"]').files.length")
        assert files_count == 1
        
        context.close()
        browser.close()
