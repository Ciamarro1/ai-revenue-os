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
        
        # Upload de mídia
        image_path = r"C:\Users\WDAGUtilityAccount\Downloads\projeto\scripts\import_user_cookies.py" # Usando arquivo temporario pequeno ou a imagem
        real_image = r"C:\Users\WDAGUtilityAccount\.gemini\antigravity\brain\4a1ba6c3-7287-4254-945d-77e07eb84017\test_pin_image_1784261880310.jpg"
        print("[+] Upload da imagem...")
        page.set_input_files("input[type='file']", os.path.abspath(real_image))
        page.wait_for_timeout(4000)
        
        # Preenchimento de campos
        print("[+] Preenchendo campos...")
        title_selector = "textarea[placeholder*='título'], textarea[placeholder*='title'], input[placeholder*='título'], [data-testid='pin-builder-title']"
        page.locator(title_selector).first.fill("AI Revenue OS Test Pin")
        
        desc_selector = "div[contenteditable='true'], textarea[placeholder*='descrição'], [data-testid='pin-builder-description']"
        page.locator(desc_selector).first.fill("Real live integration test.")
        
        link_selector = "textarea[placeholder*='link'], textarea[placeholder*='destino'], input[placeholder*='link']"
        page.locator(link_selector).first.fill("https://github.com/Ciamarro1/ai-revenue-os")
        page.wait_for_timeout(1000)
        
        # Seleciona pasta
        print("[+] Selecionando pasta...")
        board_dropdown = page.locator("button[data-testid='board-dropdown-select-button'], div[data-testid='board-dropdown-select-button'], [aria-label*='pasta'], [aria-label*='board'], div:text-is('Selecionar'), button:has-text('Selecionar')").first
        if board_dropdown.count() > 0 and board_dropdown.is_visible():
            board_dropdown.click()
            page.wait_for_timeout(2000)
            
            # Digita nome da pasta
            search_input = page.locator("input[placeholder*='Pesquisar'], input[placeholder*='Search'], input[placeholder*='pesquisar']").first
            if search_input.count() > 0 and search_input.is_visible():
                search_input.fill("AI Revenue OS")
                page.wait_for_timeout(2000)
                
                # Clica na pasta AI Revenue OS na lista
                board_option = page.locator("div[role='list'] div[role='button']:has-text('AI Revenue OS'), div[role='option']:has-text('AI Revenue OS'), text='AI Revenue OS'").last
                if board_option.count() > 0:
                    board_option.click()
                    page.wait_for_timeout(1000)
        
        # Clica em Publicar
        print("[+] Clicando em Publicar...")
        publish_btn = page.locator("text='Publicar', button:has-text('Publicar')").first
        publish_btn.click()
        
        # Tira screenshots sequenciais do processamento
        print("[+] Tirando screenshots...")
        page.wait_for_timeout(3000)
        page.screenshot(path="config/sessions/publish_step_1.png")
        
        page.wait_for_timeout(5000)
        page.screenshot(path="config/sessions/publish_step_2.png")
        
        # Lista os links na tela pós-publicação
        print("\n[+] Links e botões visíveis pós-publicação:")
        links = page.locator("a").all()
        for i, l in enumerate(links):
            try:
                href = l.get_attribute("href")
                txt = l.inner_text().strip()
                vis = l.is_visible()
                print(f"  Link {i}: Text='{txt}' | Href='{href}' | Visible={vis}")
            except Exception:
                pass
                
        buttons = page.locator("button").all()
        for i, b in enumerate(buttons):
            try:
                txt = b.inner_text().strip()
                vis = b.is_visible()
                print(f"  Button {i}: Text='{txt}' | Visible={vis}")
            except Exception:
                pass

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
