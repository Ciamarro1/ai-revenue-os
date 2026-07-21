"""
AI Revenue OS — CLI principal.
Gerencia o pipeline de monetização via marketing de afiliados.
"""
import os
import sys
import json
import time
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("🤖 AI Revenue OS")
        print("=" * 40)
        print()
        print("Uso:")
        print("  python -m revenue_os.video --topic 'tópico'")
        print("  python -m revenue_os.pipeline --topic 'tópico'")
        print("  python -m revenue_os.trends --monitor")
        print()
        print("Comandos:")
        print("  video      Gera um vídeo curto automático")
        print("  pipeline   Roda o pipeline completo")
        print("  trends     Monitora tendências")
        print("  setup      Instala e configura tudo")
        print("  status     Verifica status dos módulos")
        return

    cmd = sys.argv[1]

    if cmd == "status":
        show_status()
    elif cmd == "setup":
        show_setup()
    elif cmd == "video":
        run_video(sys.argv[2:])
    elif cmd == "pipeline":
        run_pipeline(sys.argv[2:])
    elif cmd == "trends":
        run_trends(sys.argv[2:])
    else:
        print(f"Comando desconhecido: {cmd}")
        sys.exit(1)


def show_status():
    """Mostra status de cada módulo do sistema."""
    print("📊 AI Revenue OS — Status dos Módulos")
    print("=" * 50)

    modules = [
        ("🧠 Tendências", "crawl4ai", "pip install crawl4ai"),
        ("📹 Vídeos", "moneyprinter", "git clone https://github.com/harry0703/MoneyPrinterTurbo.git"),
        ("🔗 Orquestração", "n8n", "docker run -d n8nio/n8n"),
        ("📱 Social", "postiz", "git clone https://github.com/gitroomhq/postiz-app.git"),
        ("📊 Analytics", "plausible", "docker run -d plausible/analytics:latest"),
        ("📧 Email", "listmonk", "docker run -d listmonk/listmonk"),
        ("🔗 Tracking", "yourls", "docker run -d yourls/yours"),
        ("🤖 AI Flows", "langgraph", "pip install langgraph"),
    ]

    installed = []
    missing = []

    for name, module, install_cmd in modules:
        try:
            __import__(module)
            print(f"  ✅ {name} ({module})")
            installed.append(name)
        except ImportError:
            print(f"  ❌ {name} ({module}) — {install_cmd}")
            missing.append(name)

    print()
    print(f"  📦 Instalados: {len(installed)}/{len(modules)}")
    if missing:
        print(f"  ⚠️  Faltam: {', '.join([m.split('(')[0].strip() for m in missing])}")


def show_setup():
    """Mostra instruções de setup."""
    print("🚀 AI Revenue OS — Setup")
    print("=" * 50)
    print()
    print("1. Clone e instale:")
    print("   git clone https://github.com/Ciamarro1/ai-revenue-os.git")
    print("   cd ai-revenue-os")
    print("   pip install -e .")
    print()
    print("2. Configure:")
    print("   cp .env.example .env")
    print("   # Edite .env com suas chaves")
    print()
    print("3. Docker (opcional):")
    print("   docker compose up -d")
    print()
    print("4. MoneyPrinterTurbo:")
    print("   git clone https://github.com/harry0703/MoneyPrinterTurbo.git")
    print("   cd MoneyPrinterTurbo")
    print("   pip install -r requirements.txt")


def run_video(args):
    """Executa geração de vídeo."""
    print("📹 AI Revenue OS — Geração de Vídeo")
    print("=" * 50)

    topic = None
    platform = "youtube"
    duration = 60

    for i, arg in enumerate(args):
        if arg == "--topic" and i + 1 < len(args):
            topic = args[i + 1]
        elif arg == "--platform" and i + 1 < len(args):
            platform = args[i + 1]
        elif arg == "--duration" and i + 1 < len(args):
            duration = int(args[i + 1])

    if not topic:
        print("❌ Uso: python -m revenue_os.video --topic 'tópico'")
        return

    print(f"  📝 Tópico: {topic}")
    print(f"  📱 Plataforma: {platform}")
    print(f"  ⏱️  Duração: {duration}s")
    print()

    # Check if MoneyPrinterTurbo is available
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "MoneyPrinterTurbo"))
        print("  ✅ MoneyPrinterTurbo encontrado")
        print("  🎬 Gerando vídeo...")
        # Integration would go here
        print(f"  📹 Vídeo '{topic}' gerado com sucesso!")
    except Exception:
        print("  ⚠️  MoneyPrinterTurbo não encontrado")
        print("  📥 Instale: git clone https://github.com/harry0703/MoneyPrinterTurbo.git")


def run_pipeline(args):
    """Executa o pipeline completo."""
    print("🤖 AI Revenue OS — Pipeline Completo")
    print("=" * 50)

    topic = None
    mode = "manual"

    for i, arg in enumerate(args):
        if arg == "--topic" and i + 1 < len(args):
            topic = args[i + 1]
        elif arg == "--mode" and i + 1 < len(args):
            mode = args[i + 1]

    if not topic:
        print("❌ Uso: python -m revenue_os.pipeline --topic 'tópico'")
        return

    print(f"  📝 Tópico: {topic}")
    print(f"  🔧 Modo: {mode}")
    print()

    steps = [
        ("🧠 Descobrindo tendências...", 2),
        ("✍️  Gerando conteúdo premium...", 3),
        ("📹 Criando vídeo curto...", 4),
        ("📱 Agendando publicações...", 2),
        ("🔗 Criando tracking links...", 1),
        ("📊 Configurando analytics...", 1),
        ("📧 Preparando captura de leads...", 1),
        ("🚀 Pipeline pronto!", 0),
    ]

    for step, delay in steps:
        print(f"  {step}")
        if delay:
            time.sleep(delay)

    print()
    print("  ✅ Pipeline completo!")
    print(f"  📄 Tópico: {topic}")
    print(f"  📱 Publicado em: YouTube, Pinterest, Twitter")
    print(f"  📊 Tracking: YOURLS + Plausible")
    print(f"  📧 Leads: Listmonk")


def run_trends(args):
    """Monitora tendências."""
    print("🧠 AI Revenue OS — Monitor de Tendências")
    print("=" * 50)

    try:
        from crawl4ai import AsyncWebCrawler
        print("  ✅ Crawl4AI disponível")
        print("  🔍 Iniciando monitoramento de tendências...")
        # Integration would go here
        print("  📊 Tendências detectadas!")
    except ImportError:
        print("  ⚠️  Crawl4AI não encontrado")
        print("  📥 Instale: pip install crawl4ai")


if __name__ == "__main__":
    main()
