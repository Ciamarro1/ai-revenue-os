import os
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class NvidiaImageGenerator:
    """
    Gerador de Imagens de Alta Qualidade utilizando a API do NVIDIA Catalog NIMs.
    Conectado ao modelo FLUX.1-dev para geração de alta fidelidade e fotorrealismo.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.api_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"

    def generate(self, prompt: str, output_path: str, width: int = 1024, height: int = 1024, steps: int = 30, seed: int = 0) -> bool:
        """
        Gera uma imagem a partir de um prompt de texto e salva no caminho indicado.
        """
        if not self.api_key or "nvapi-" not in self.api_key:
            print("❌ Erro: NVIDIA_API_KEY não configurada no ambiente (.env).")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "seed": seed
        }

        print(f"[NvidiaImageGenerator] Enviando prompt para FLUX.1-dev (NVIDIA)...")
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
        except Exception as e:
            print(f"[ERROR] Falha de rede ao conectar à NVIDIA API: {str(e)}")
            return False

        if response.status_code != 200:
            print(f"[ERROR] Erro na API do NVIDIA Catalog (HTTP {response.status_code}): {response.text}")
            return False

        data = response.json()
        artifacts = data.get("artifacts", [])
        
        if not artifacts:
            print(f"[ERROR] Resposta da API não contém artefatos de imagem: {data}")
            return False

        # Extrai os dados base64 da primeira imagem gerada
        base64_str = artifacts[0].get("base64")
        if not base64_str:
            print("[ERROR] Artefato de imagem não contém dados base64 válidos.")
            return False

        # Salva o arquivo de imagem localmente
        try:
            image_bytes = base64.b64decode(base64_str)
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "wb") as f:
                f.write(image_bytes)
            print(f"[SUCCESS] Imagem gerada e salva com sucesso em: {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Erro ao decodificar/gravar arquivo de imagem: {str(e)}")
            return False
