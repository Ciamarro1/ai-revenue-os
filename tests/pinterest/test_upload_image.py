import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

def test_mock_upload_image(mock_html_path, dummy_image):
    """
    Testa se o Playwright consegue selecionar e definir o arquivo de imagem no input file (Sprint P2 - Passo 2.1).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        mock_url = mock_html_path.resolve().as_uri()
        page.goto(mock_url)
        
        # Seleciona o input e faz o upload
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(str(dummy_image))
        
        # Verifica se o arquivo foi atrelado
        # Em HTML5 inputs de arquivo armazenam os itens no array 'files' da DOM
        files_count = page.evaluate("document.querySelector('input[type=\"file\"]').files.length")
        assert files_count == 1
        
        context.close()
        browser.close()
