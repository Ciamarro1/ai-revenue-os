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
        page.wait_for_timeout(10000) # Espera 10s para carregar tudo (React, imagens, banners)
        
        screenshot_path = Path("config/sessions/debug_screenshot.png")
        page.screenshot(path=str(screenshot_path))
        print(f"[+] Screenshot salva em: {screenshot_path.resolve()}")
        
        # Lista botões e inputs visíveis para nos orientar
        print("\n[+] Analisando elementos na tela:")
        buttons = page.locator("button").all()
        print(f"Botoes encontrados ({len(buttons)}):")
        for i, btn in enumerate(buttons[:15]):
            try:
                txt = btn.inner_text().strip()
                vis = btn.is_visible()
                aria = btn.get_attribute("aria-label")
                print(f"  {i}. Text: '{txt}' | Visible: {vis} | Aria-label: '{aria}'")
            except Exception:
                pass
                
        inputs = page.locator("input, textarea, div[contenteditable='true']").all()
        print(f"\nInputs/Textareas/Editables encontrados ({len(inputs)}):")
        for i, inp in enumerate(inputs[:15]):
            try:
                tag = inp.evaluate("el => el.tagName")
                placeholder = inp.get_attribute("placeholder")
                tid = inp.get_attribute("data-testid")
                vis = inp.is_visible()
                print(f"  {i}. Tag: {tag} | data-testid: '{tid}' | Placeholder: '{placeholder}' | Visible: {vis}")
            except Exception:
                pass

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
