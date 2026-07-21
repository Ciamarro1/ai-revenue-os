import os
import sys
import time
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
        page.wait_for_timeout(6000)
        
        print("[+] Fechando modal de tutorial...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(2000)
        
        # 1. SELECIONA OU CRIA PASTA
        print("[+] Verificando pasta selecionada...")
        already_selected = page.locator("div[role='button']").filter(has_text="AI Revenue OS")
        if already_selected.count() > 0 and already_selected.first.is_visible():
            print("[+] Pasta 'AI Revenue OS' ja esta selecionada! Pulando selecao.")
        else:
            print("[+] Selecionando pasta no dropdown...")
            # Localiza o dropdown pelo texto ou testid
            # Localiza o dropdown pelo texto ou testid de forma robusta
            board_dropdown = page.locator("div[role='button']").filter(has_text="Selecionar").first
            board_dropdown.wait_for(state="visible", timeout=10000)
            board_dropdown.click()
            page.wait_for_timeout(2500)
            
            # Pesquisa por "AI Revenue OS"
            search_input = page.locator("input[placeholder*='Pesquisar'], input[placeholder*='Search'], input[placeholder*='pesquisar']").first
            search_input.wait_for(state="visible", timeout=5000)
            search_input.fill("AI Revenue OS")
            page.wait_for_timeout(3000) # Aguarda busca
            
            # Verifica se mostra no-results
            no_results = page.locator("text='Nenhuma pasta encontrada', text='No boards found'")
            if no_results.count() > 0 and no_results.first.is_visible():
                print("[+] Pasta 'AI Revenue OS' nao existe. Criando...")
                create_btn = page.locator("text='Criar pasta'").first
                create_btn.click()
                page.wait_for_timeout(2500)
                
                # Digita nome da pasta
                board_name_input = page.locator("input[placeholder*='Lugares'], input[placeholder*='Receitas'], input[id*='board-name']").first
                board_name_input.fill("AI Revenue OS")
                page.wait_for_timeout(1000)
                
                # Confirma criação
                create_confirm = page.locator("button:text-is('Criar')").first
                create_confirm.click()
                page.wait_for_timeout(5000) # Aguarda criação
            else:
                # Pasta existe, clica nela na lista
                print("[+] Pasta encontrada no dropdown. Clicando...")
                board_option = page.locator("div[role='list'] div[role='button']:has-text('AI Revenue OS'), div[role='option']:has-text('AI Revenue OS'), text='AI Revenue OS'").last
                if board_option.count() > 0:
                    board_option.click()
                else:
                    print("[+] Selecionando pasta via teclado (ArrowDown + Enter)...")
                    page.keyboard.press("ArrowDown")
                    page.keyboard.press("Enter")
                page.wait_for_timeout(2000)

        # 2. PREENCHE OS CAMPOS DE TEXTO
        print("[+] Preenchendo campos de texto...")
        title_selector = "textarea[placeholder*='título'], textarea[placeholder*='title'], input[placeholder*='título'], [data-testid='pin-builder-title']"
        page.locator(title_selector).first.fill("AI Revenue OS - Automation Lab")
        page.wait_for_timeout(1000)
        
        desc_selector = "div[contenteditable='true'], textarea[placeholder*='descrição'], [data-testid='pin-builder-description']"
        page.locator(desc_selector).first.fill("Este eh um Pin de teste publicado de forma 100% automatizada pelo laboratorio autonomo do AI Revenue OS.")
        page.wait_for_timeout(1000)
        
        link_selector = "textarea[placeholder*='link'], textarea[placeholder*='destino'], input[placeholder*='link']"
        page.locator(link_selector).first.fill("https://github.com/Ciamarro1/ai-revenue-os")
        page.wait_for_timeout(1000)
        
        # 3. REALIZA UPLOAD DA IMAGEM
        real_image = r"C:\Users\WDAGUtilityAccount\.gemini\antigravity\brain\4a1ba6c3-7287-4254-945d-77e07eb84017\test_pin_image_1784261880310.jpg"
        print(f"[+] Realizando upload da imagem: {real_image}")
        page.set_input_files("input[type='file']", os.path.abspath(real_image))
        page.wait_for_timeout(8000) # Aguarda upload completo da imagem
        
        # 4. PUBLICA
        print("[+] Clicando em Publicar...")
        publish_btn = page.locator("div[role='button']:has-text('Publicar'), button:has-text('Publicar')").first
        publish_btn.wait_for(state="visible", timeout=10000)
        publish_btn.click()
        
        print("[+] Aguardando confirmacao (toast de sucesso)...")
        page.wait_for_timeout(8000)
        
        # Captura screenshot final
        page.screenshot(path="config/sessions/publish_final_success.png")
        
        # Tenta extrair a URL do Pin publicado na toast de sucesso
        try:
            toast_link = page.locator("a[href*='/pin/']").first
            toast_link.wait_for(state="visible", timeout=15000)
            pin_url = toast_link.get_attribute("href")
            if pin_url:
                if pin_url.startswith("/"):
                    pin_url = "https://www.pinterest.com" + pin_url
                print(f"==============================================================")
                print(f"SUCCESS! PIN PUBLICADO AO VIVO!")
                print(f"URL DO PIN: {pin_url}")
                print(f"==============================================================")
                
                # Salva o resultado em arquivo para auditoria
                with open("config/sessions/last_published_pin.txt", "w") as f:
                    f.write(pin_url)
            else:
                print("[-] Nao foi possivel extrair o href da toast de sucesso.")
        except Exception as e:
            print(f"[-] Nao foi possivel localizar a toast de sucesso com link do Pin: {e}")
            print(f"URL final da pagina: {page.url}")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
