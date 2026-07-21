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
        
        print("[+] Abrindo dropdown de pasta...")
        board_dropdown = page.locator("button[data-testid='board-dropdown-select-button'], div[data-testid='board-dropdown-select-button'], [aria-label*='pasta'], [aria-label*='board'], div:text-is('Selecionar'), button:has-text('Selecionar')").first
        board_dropdown.click()
        page.wait_for_timeout(2000)
        
        print("[+] Clicando em 'Criar pasta'...")
        create_btn = page.locator("text='Criar pasta'").first
        create_btn.click()
        page.wait_for_timeout(3000)
        
        page.screenshot(path="config/sessions/debug_create_board_modal.png")
        print("[+] Screenshot do modal de criacao de pasta salvo!")

        # Encontra inputs no modal
        print("\n[+] Analisando elementos no modal de criacao:")
        inputs = page.locator("input, button").all()
        for i, inp in enumerate(inputs):
            try:
                tag = inp.evaluate("el => el.tagName")
                txt = inp.inner_text().strip()
                placeholder = inp.get_attribute("placeholder")
                vis = inp.is_visible()
                print(f"  Item {i}: Tag={tag} | Visible={vis} | Text='{txt[:30]}' | Placeholder='{placeholder}'")
            except Exception:
                pass

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
