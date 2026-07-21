import time
import requests
from pathlib import Path
from typing import Dict, Any
from src.integrations.pinterest.errors import PinterestUploadError, UploadTimeoutError

class VideoUploader:
    """
    Componente especializado para o fluxo de upload multipart de vídeo do Pinterest.
    """
    
    def __init__(self, auth_headers: Dict[str, str], rate_limit_mgr):
        self.headers = auth_headers
        self.rate_limit_mgr = rate_limit_mgr

    def upload_video(self, video_path: str) -> str:
        """
        Executa o pipeline completo: registro -> post S3 -> polling de processamento.
        Retorna o media_id pronto para publicação.
        """
        path = Path(video_path)
        if not path.exists():
            raise PinterestUploadError(f"Arquivo de vídeo não encontrado no caminho: {video_path}")

        # 1. Registrar o Upload
        print("🎬 [VideoUploader] Registrando upload de mídia no Pinterest...")
        register_url = "https://api.pinterest.com/v5/media"
        reg_payload = {"media_type": "video"}
        
        self.rate_limit_mgr.check_and_wait("pinterest")
        response = requests.post(register_url, json=reg_payload, headers=self.headers)
        
        # Envia headers de rate limit ao manager
        self._update_rate_limits(response.headers)
        
        if response.status_code == 429:
            reset_ts = float(response.headers.get("x-ratelimit-reset", time.time() + 60))
            self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
            # Tenta novamente após a espera
            response = requests.post(register_url, json=reg_payload, headers=self.headers)

        if response.status_code != 201:
            raise PinterestUploadError(f"Falha ao registrar mídia no Pinterest: {response.text}")
            
        reg_data = response.json()
        media_id = reg_data["media_id"]
        upload_url = reg_data["upload_url"]
        upload_parameters = reg_data["upload_parameters"]

        # 2. Upload para o S3
        print(f"🎬 [VideoUploader] Realizando POST para o bucket S3 do Pinterest (Media ID: {media_id})...")
        try:
            with open(path, "rb") as video_file:
                # Os parâmetros do S3 precisam ir antes do arquivo no multipart/form-data
                files = {"file": video_file}
                s3_response = requests.post(upload_url, data=upload_parameters, files=files)
                
            if s3_response.status_code not in (200, 201, 204):
                raise PinterestUploadError(f"Falha no upload para o S3 do Pinterest: {s3_response.text}")
        except Exception as e:
            if not isinstance(e, PinterestUploadError):
                raise PinterestUploadError(f"Erro ao transmitir arquivo para o S3: {str(e)}")
            raise e

        # 3. Polling de Processamento
        print("🎬 [VideoUploader] Aguardando processamento do vídeo no Pinterest...")
        max_attempts = 30
        interval = 5
        poll_url = f"https://api.pinterest.com/v5/media/{media_id}"
        
        for attempt in range(1, max_attempts + 1):
            time.sleep(interval)
            print(f"🎬 [VideoUploader] Verificando status... Tentativa {attempt}/{max_attempts}")
            
            self.rate_limit_mgr.check_and_wait("pinterest")
            poll_resp = requests.get(poll_url, headers=self.headers)
            self._update_rate_limits(poll_resp.headers)
            
            if poll_resp.status_code == 200:
                status_data = poll_resp.json()
                status = status_data.get("status")
                
                if status == "succeeded":
                    print(f"✅ [VideoUploader] Vídeo processado com sucesso (Media ID: {media_id})!")
                    return media_id
                elif status == "failed":
                    raise PinterestUploadError("Pinterest reportou falha no processamento do vídeo.")
            elif poll_resp.status_code == 429:
                reset_ts = float(poll_resp.headers.get("x-ratelimit-reset", time.time() + 60))
                self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
                
        raise UploadTimeoutError(f"Timeout excedido ({max_attempts * interval}s) no processamento do vídeo no Pinterest.")

    def _update_rate_limits(self, headers: Dict[str, str]):
        """Repassa as informações de rate limit dos headers HTTP para o manager."""
        limit = headers.get("x-ratelimit-limit")
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        
        if limit is not None and remaining is not None and reset is not None:
            self.rate_limit_mgr.update_limits(
                platform="pinterest",
                limit_val=limit,
                remaining=remaining,
                reset_timestamp=reset
            )



