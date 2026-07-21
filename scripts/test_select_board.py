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
        
        # Procura o dropdown de pasta (board)
        # Na screenshot vemos o texto "Selecionar" na esquerda de "Publicar"
        print("[+] Procurando dropdown de pasta...")
        board_dropdown = page.locator("button[data-testid='board-dropdown-select-button'], div[data-testid='board-dropdown-select-button'], [aria-label*='pasta'], [aria-label*='board'], div:text-is('Selecionar'), button:has-text('Selecionar')").first
        
        if board_dropdown.count() > 0 and board_dropdown.is_visible():
            print("[+] Clicando no dropdown de pasta...")
            board_dropdown.click()
            page.wait_for_timeout(2000)
            
            # Tira screenshot com o dropdown aberto
            page.screenshot(path="config/sessions/debug_board_dropdown_open.png")
            print("[+] Screenshot do dropdown salvo!")
            
            # Lista os elementos do dropdown
            print("\n[+] Elementos do dropdown:")
            board_items = page.locator("[role='option'], div[data-testid*='board'], div:has-text('Pasta'), div:has-text('Board')").all()
            for i, item in enumerate(board_items[:15]):
                try:
                    txt = item.inner_text().strip()
                    vis = item.is_visible()
                    print(f"  Item {i}: Text='{txt}' | Visible={vis}")
                except Exception:
                    pass
            
            # Clicar na primeira opção de pasta disponível
            # Geralmente as pastas aparecem em uma lista de divs clicáveis
            first_board = page.locator("div[role='list'] div[role='button'], div[data-testid*='board-option'], div[role='option']").first
            if first_board.count() > 0:
                print(f"[+] Selecionando a primeira pasta encontrada...")
                first_board.click()
                page.wait_for_timeout(1000)
            else:
                # Se não achou com o locator estrito, clica no primeiro item da lista visível que não seja cabeçalho
                print("[+] Tentando clicar no primeiro elemento clicável da lista...")
                page.keyboard.press("Tab") # Às vezes foca a pesquisa
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                page.wait_for_timeout(1000)
                
            page.screenshot(path="config/sessions/debug_board_selected.png")
            print("[+] Screenshot após seleção de pasta salvo!")
        else:
            print("[-] Dropdown de pasta nao encontrado ou nao visivel.")

        context.close()
        browser.close()

if __name__ == "__main__":
    main()
