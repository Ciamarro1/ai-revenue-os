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
        
        # Encontra o botão de Publicar
        publish_btn = page.locator("text='Publicar', button:has-text('Publicar')").first
        print(f"[+] Botao Publicar encontrado? {publish_btn.count() > 0}")
        
        # Lista todos os elementos clicáveis que estão próximos ao botão Publicar
        # ou que parecem ser o dropdown
        print("\n[+] Analisando elementos clicáveis na região superior do Pin Builder:")
        elements = page.locator("button, div[role='button'], div[data-testid]").all()
        for i, el in enumerate(elements):
            try:
                txt = el.inner_text().strip().replace("\n", " ")
                vis = el.is_visible()
                tid = el.get_attribute("data-testid")
                role = el.get_attribute("role")
                aria = el.get_attribute("aria-label")
                if vis and len(txt) < 100:
                    print(f"  El {i}: Tag={el.evaluate('el => el.tagName')} | Text='{txt}' | testid='{tid}' | role='{role}' | aria='{aria}'")
            except Exception:
                pass

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
