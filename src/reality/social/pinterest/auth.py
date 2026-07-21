import os
from typing import Dict
from src.integrations.pinterest.errors import PinterestAuthError

class PinterestAuth:
    """
    Gerencia as credenciais do Pinterest (OAuth 2.0 Access Token manual).
    """
    
    def __init__(self, access_token: str = None):
        self._access_token = access_token or os.getenv("PINTEREST_ACCESS_TOKEN")
        if not self._access_token or "your_token" in self._access_token:
            raise PinterestAuthError("Token de acesso do Pinterest não configurado no ambiente (.env).")
            
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Retorna os cabeçalhos de autenticação necessários para a API v5 do Pinterest.
        """
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json"
        }



