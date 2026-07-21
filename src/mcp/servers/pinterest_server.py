import os
from src.mcp.registry import MCPServer
from src.integrations.pinterest.errors import PinterestAuthError

class PinterestServer(MCPServer):
    """
    Integração do Pinterest que delega todas as ações ao cliente canônico resiliente.
    """
    def __init__(self):
        super().__init__("PinterestServer")
        self.client = None
        
        # Capacidade 1: Publicação de Imagem/Vídeo Curto
        self.register_tool(
            "publish_pin",
            "Publica o ativo gerado na plataforma Pinterest.",
            self.publish_pin
        )
        
        # Capacidade 2: Coleta de Métricas
        self.register_tool(
            "get_pin_metrics",
            "Recupera views, clicks e saves de um Pin específico.",
            self.get_pin_metrics
        )
        
        # Capacidade 3: Listagem Recente
        self.register_tool(
            "list_recent_publications",
            "Lista campanhas ativas geradas pelo sistema recentemente.",
            self.list_recent_publications
        )
        
        # Capacidade 4: Arquivamento
        self.register_tool(
            "archive_campaign",
            "Pausa/Deleta um pin quando o Decision Engine mandar um KILL ou EXIT.",
            self.archive_campaign
        )

    def _get_client(self):
        """Instancia o PinterestClient de forma preguiçosa (lazy) para evitar crashes em testes sem .env."""
        if self.client is None:
            from src.integrations.pinterest.client import PinterestClient
            # Se não estiver no ambiente real e faltar token, usa um mock token no modo shadow para segurança
            token = os.getenv("PINTEREST_ACCESS_TOKEN")
            if not token or "your_token" in token:
                # Se estivermos rodando testes de infraestrutura sem token real
                self.client = PinterestClient(mode="shadow", access_token="mock_token_for_tests", board_id="mock_board")
            else:
                self.client = PinterestClient()
        return self.client

    def publish_pin(self, media_path: str, title: str, description: str, destination_link: str) -> dict:
        client = self._get_client()
        ext = os.path.splitext(media_path)[1].lower()
        
        if ext == ".mp4":
            res = client.publish_video(media_path, title, description, destination_link)
        else:
            res = client.publish_image(media_path, title, description, destination_link)
            
        return {
            "status": "success",
            "platform_id": res.content_id,
            "url": res.url,
            "published_status": res.status
        }

    def get_pin_metrics(self, platform_id: str) -> dict:
        client = self._get_client()
        res = client.get_metrics(platform_id)
        return {
            "impressions": res.impressions,
            "outbound_clicks": res.outbound_clicks,
            "saves": res.saves
        }
        
    def list_recent_publications(self, limit: int = 10) -> list:
        # Se for shadow, retorna uma lista simulada baseada no mock padrão
        client = self._get_client()
        if client.mode == "shadow":
            return [{"platform_id": "SHADOW-PIN-MOCK", "status": "active"}]
            
        # Para live, retornaria pins do board (v5 GET /boards/{board_id}/pins)
        url = f"https://api.pinterest.com/v5/boards/{client.board_id}/pins"
        client.rate_limit_mgr.check_and_wait("pinterest")
        import requests
        response = requests.get(url, headers=client.headers, params={"page_size": limit})
        client._update_rate_limits(response.headers)
        
        if response.status_code == 200:
            items = response.json().get("items", [])
            return [{"platform_id": i["id"], "status": "active"} for i in items]
        return []
        
    def archive_campaign(self, platform_id: str) -> bool:
        client = self._get_client()
        return client.archive_content(platform_id)



