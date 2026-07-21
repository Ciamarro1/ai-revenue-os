import sys
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.services.image_generator import NvidiaImageGenerator

def main():
    parser = argparse.ArgumentParser(description="Gerador de Imagens via NVIDIA API (FLUX.1-dev)")
    parser.add_argument("prompt", help="Prompt descritivo para gerar a imagem")
    parser.add_argument("output", help="Caminho do arquivo de saída (ex: output.jpg ou output.png)")
    parser.add_argument("--width", type=int, default=1024, help="Largura da imagem (padrão: 1024)")
    parser.add_argument("--height", type=int, default=1024, help="Altura da imagem (padrão: 1024)")
    parser.add_argument("--steps", type=int, default=30, help="Passos de inferência (padrão: 30)")
    parser.add_argument("--seed", type=int, default=0, help="Semente de geração (padrão: 0)")

    args = parser.parse_args()

    generator = NvidiaImageGenerator()
    success = generator.generate(
        prompt=args.prompt,
        output_path=args.output,
        width=args.width,
        height=args.height,
        steps=args.steps,
        seed=args.seed
    )

    if success:
        print("[SUCCESS] Geração de imagem finalizada com sucesso!")
    else:
        print("[ERROR] Falha na geração da imagem.")
        sys.exit(1)

if __name__ == "__main__":
    main()
