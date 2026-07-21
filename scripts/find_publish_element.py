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
        
        # Encontra elementos com texto "Publicar" ou "Avançar"
        print("[+] Procurando elementos contendo 'Publicar'...")
        elements = page.locator("*:has-text('Publicar')").all()
        for i, el in enumerate(elements):
            try:
                tag = el.evaluate("el => el.tagName")
                classes = el.evaluate("el => el.className")
                text = el.inner_text().strip()
                vis = el.is_visible()
                print(f"Match {i}: Tag={tag} | Visible={vis} | Text='{text[:30]}' | Class='{classes[:50]}'")
            except Exception:
                pass
                
        context.close()
        browser.close()

if __name__ == "__main__":
    main()
