import os
import sys
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv()

from src.integrations.pinterest.client import PinterestClient
from src.integrations.pinterest.errors import PinterestError

def main():
    parser = argparse.ArgumentParser(description="Operador de Validação do Pinterest MCP")
    parser.add_argument("action", choices=["health", "publish-image", "publish-video", "get-metrics"],
                        help="Ação a ser executada no Pinterest")
    parser.add_argument("--path", help="Caminho do arquivo local (imagem ou vídeo)")
    parser.add_argument("--title", default="AI Revenue OS Test", help="Título do Pin")
    parser.add_argument("--desc", default="Teste automatizado de integração resiliente.", help="Descrição do Pin")
    parser.add_argument("--link", default="https://github.com/Ciamarro1/ai-revenue-os", help="Link de destino")
    parser.add_argument("--id", help="Pin ID para consulta de métricas")
    parser.add_argument("--live", action="store_true", help="Força a execução em modo LIVE (ignora PINTEREST_MODE=shadow)")

    args = parser.parse_args()

    # Configura o modo com base no argumento --live ou no .env
    mode = "live" if args.live else os.getenv("PINTEREST_MODE", "shadow").lower()
    
    print(f"⚙️  Inicializando PinterestClient em modo: {mode.upper()}...")
    try:
        client = PinterestClient(mode=mode)
    except Exception as e:
        print(f"❌ Falha de Autenticação/Inicialização: {str(e)}")
        sys.exit(1)

    if args.action == "health":
        print("🔍 Executando Health Check do provedor Pinterest...")
        status = client.health()
        print("\n📋 Resultado do Health Check:")
        for k, v in status.items():
            print(f"  - {k}: {v}")
            
    elif args.action == "publish-image":
        if not args.path:
            print("❌ Erro: Informe o caminho da imagem com --path")
            sys.exit(1)
        print(f"📤 Publicando Imagem: {args.path}")
        try:
            res = client.publish_image(args.path, args.title, args.desc, args.link)
            print(f"✅ Sucesso! Pin ID: {res.content_id} | Status: {res.status} | URL: {res.url}")
        except PinterestError as e:
            print(f"❌ Falha na publicação da imagem: {str(e)}")
            sys.exit(1)
            
    elif args.action == "publish-video":
        if not args.path:
            print("❌ Erro: Informe o caminho do vídeo com --path")
            sys.exit(1)
        print(f"📤 Iniciando upload e publicação de Vídeo: {args.path}")
        try:
            res = client.publish_video(args.path, args.title, args.desc, args.link)
            print(f"✅ Sucesso! Pin ID: {res.content_id} | Status: {res.status} | URL: {res.url}")
        except PinterestError as e:
            print(f"❌ Falha na publicação do vídeo: {str(e)}")
            sys.exit(1)
            
    elif args.action == "get-metrics":
        if not args.id:
            print("❌ Erro: Informe o Pin ID com --id")
            sys.exit(1)
        print(f"📊 Consultando métricas para o Pin ID: {args.id}")
        try:
            metrics = client.get_metrics(args.id)
            print(f"\n📋 Métricas Canônicas:")
            print(f"  - Impressões: {metrics.impressions}")
            print(f"  - Cliques Externos: {metrics.outbound_clicks}")
            print(f"  - Salvos: {metrics.saves}")
        except PinterestError as e:
            print(f"❌ Falha ao obter métricas: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main()
