import os
import sys
import logging
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

# Habilita log no terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

from src.execution.publisher.pinterest_playwright import PinterestPlaywrightPublisher

def main():
    print("==============================================================")
    print(" [AI Revenue OS] PUBLICADOR REAL DE TESTE (VIA PLAYWRIGHT) ")
    print("==============================================================")

    # Imagem gerada pelo Antigravity
    image_path = r"C:\Users\WDAGUtilityAccount\.gemini\antigravity\brain\4a1ba6c3-7287-4254-945d-77e07eb84017\test_pin_image_1784261880310.jpg"
    
    if not os.path.exists(image_path):
        print(f"[-] Imagem de teste nao encontrada em: {image_path}")
        sys.exit(1)

    publisher = PinterestPlaywrightPublisher()
    
    payload = {
        "media_path": image_path,
        "title": "AI Revenue OS Live Integration Test",
        "description": "Este eh um Pin real publicado via automacao deterministica pelo AI Revenue OS.",
        "link": "https://github.com/Ciamarro1/ai-revenue-os",
        "headless": False  # Rodamos no modo VISIVEL para que o usuario veja acontecer ao vivo!
    }

    print("\n[+] Iniciando publicacao ao vivo no Pinterest...")
    try:
        res = publisher.publish(payload)
        print("\n==============================================================")
        if res.get("status") == "success":
            print("SUCCESS!")
            print(f"  - Pin ID: {res.get('pin_id')}")
            print(f"  - URL do Pin: {res.get('url')}")
            print("==============================================================")
        else:
            print("[-] FALHA NA PUBLICACAO:")
            print(f"  - Erro: {res.get('error')}")
            print("==============================================================")
            sys.exit(1)
    except Exception as e:
        print(f"\n[-] Excecao Inesperada durante a publicacao: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
