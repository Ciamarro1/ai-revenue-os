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
        
        print("[+] Fechando modal...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(2000)
        
        # Upload de mídia para liberar o form
        image_path = r"C:\Users\WDAGUtilityAccount\.gemini\antigravity\brain\4a1ba6c3-7287-4254-945d-77e07eb84017\test_pin_image_1784261880310.jpg"
        print("[+] Fazendo upload...")
        page.set_input_files("input[type='file']", os.path.abspath(image_path))
        page.wait_for_timeout(3000)
        
        print("[+] Abrindo dropdown de pasta...")
        board_dropdown = page.locator("button[data-testid='board-dropdown-select-button'], div[data-testid='board-dropdown-select-button'], [aria-label*='pasta'], [aria-label*='board'], div:text-is('Selecionar'), button:has-text('Selecionar')").first
        board_dropdown.click()
        page.wait_for_timeout(2000)
        
        print("[+] Clicando em 'Criar pasta'...")
        create_btn = page.locator("text='Criar pasta'").first
        create_btn.click()
        page.wait_for_timeout(2000)
        
        print("[+] Preenchendo nome da pasta...")
        board_name_input = page.locator("input[placeholder*='Lugares'], input[placeholder*='Receitas'], input[id*='board-name']").first
        board_name_input.fill("AI Revenue OS")
        page.wait_for_timeout(1000)
        
        page.screenshot(path="config/sessions/debug_before_create_confirm.png")
        print("[+] Screenshot antes de confirmar criacao salvo!")
        
        print("[+] Confirmando criacao...")
        create_confirm_btn = page.locator("button:text-is('Criar')").first
        create_confirm_btn.click()
        
        page.wait_for_timeout(4000) # Espera 4s para a criacao processar
        
        page.screenshot(path="config/sessions/debug_after_create_confirm.png")
        print("[+] Screenshot pos-confirmacao salvo!")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
