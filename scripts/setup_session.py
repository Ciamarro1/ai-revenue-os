import os
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def setup_session(platform: str):
    print("==============================================================")
    print(f" [AI Revenue OS] INITIAL SESSION SETUP: {platform.upper()} ")
    print("==============================================================")
    
    sessions_dir = Path("config/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_file = sessions_dir / f"{platform}.json"
    
    urls = {
        "pinterest": "https://www.pinterest.com/login/"
    }
    
    url = urls.get(platform, "https://www.google.com")
    
    print("\n1. Iniciando navegador em modo visível (headful)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"2. Acessando {url}...")
        page.goto(url)
        
        print("\n==============================================================")
        print(" ATENÇÃO: Faça o login manualmente na janela do navegador.")
        print(" Quando terminar e estiver na tela inicial logada,")
        print(" volte aqui e pressione ENTER no terminal para salvar a sessão.")
        print("==============================================================")
        
        input("\nPressione ENTER após realizar o login com sucesso...")
        
        # Salva o estado da sessão (cookies, localStorage, etc.)
        context.storage_state(path=str(session_file))
        print(f"\n✅ Sessão salva com sucesso em: {session_file}")
        
        context.close()
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utilitário de setup de sessão persistente para publicação")
    parser.add_argument("--platform", type=str, default="pinterest", help="Plataforma de rede social")
    args = parser.parse_args()
    
    setup_session(args.platform)
