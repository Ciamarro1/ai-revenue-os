import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

def main():
    session_path = Path("config/sessions/pinterest.json")
    if not session_path.exists():
        print("[-] config/sessions/pinterest.json nao encontrado!")
        return

    with sync_playwright() as p:
        print("[+] Abrindo Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=str(session_path),
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print("[+] Navegando para pin-builder...")
        page.goto("https://www.pinterest.com/pin-builder/", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        
        # Tenta fechar o modal usando Escape
        print("[+] Enviando tecla 'Escape'...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(2000)
        
        # Tenta clicar no botão Cancelar se ainda visível
        cancel_btn = page.locator("button[aria-label='Cancelar'], button[aria-label='Fechar'], button[aria-label='Close']")
        if cancel_btn.count() > 0 and cancel_btn.first.is_visible():
            print("[+] Clicando no botao de fechar/cancelar...")
            cancel_btn.first.click()
            page.wait_for_timeout(2000)
            
        screenshot_path = Path("config/sessions/debug_screenshot_after_modal.png")
        page.screenshot(path=str(screenshot_path))
        print(f"[+] Screenshot pós-fechamento salva em: {screenshot_path.resolve()}")
        
        # Verifica se o input de arquivo agora está visível e disponível
        file_input = page.locator("input[type='file']")
        print(f"[+] Input de arquivo encontrado e visivel? {file_input.count() > 0 and file_input.first.is_visible()}")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
