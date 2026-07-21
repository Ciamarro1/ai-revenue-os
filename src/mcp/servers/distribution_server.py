from src.mcp.registry import MCPServer

class DistributionServer(MCPServer):
    def __init__(self):
        super().__init__("DistributionServer")
        self.register_tool(
            "publish_video",
            "Faz upload do render_result.mp4 para plataformas alvo (TikTok, YT Shorts).",
            self.publish_video
        )
        self.register_tool(
            "get_campaign_status",
            "Verifica o status da submissão na rede social.",
            self.get_campaign_status
        )

    def publish_video(self, platform: str, video_path: str, metadata: dict):
        # Abstração de API do YouTube/TikTok
        pass

    def get_campaign_status(self, campaign_id: str):
        pass
