class MCPServer:
    """Base class for all Model Context Protocol (MCP) servers."""
    def __init__(self, name: str):
        self.name = name
        self.tools = {}

    def register_tool(self, name: str, description: str, handler: callable):
        self.tools[name] = {
            "description": description,
            "handler": handler
        }

    def get_available_tools(self) -> dict:
        return {
            "server": self.name,
            "tools": [{"name": k, "description": v["description"]} for k, v in self.tools.items()]
        }
        
    def execute_tool(self, name: str, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found in {self.name}")
        return self.tools[name]["handler"](**kwargs)

class MCPRegistry:
    """
    O Registro de Ferramentas. 
    Os agentes LLMs interrogam o Registry ("Quais ferramentas estão disponíveis?")
    e ele retorna a lista de tools agregada de todos os servidores.
    """
    def __init__(self):
        self.servers = {}
        
    def register_server(self, server: MCPServer):
        self.servers[server.name] = server
        
    def list_all_tools(self) -> list:
        all_tools = []
        for server_name, server in self.servers.items():
            all_tools.append(server.get_available_tools())
        return all_tools
        
    def route_call(self, server_name: str, tool_name: str, **kwargs):
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not registered.")
        return self.servers[server_name].execute_tool(tool_name, **kwargs)

from src.mcp.health_monitor import HealthMonitor

class CapabilityRegistry:
    """
    Abstrai os Servidores MCP. 
    Os Agentes pedem uma 'Capacidade' (Ex: publish_short_video) e o registro
    localiza qual provedor de MCP (Youtube, Tiktok) a oferece.
    """
    def __init__(self, mcp_registry: MCPRegistry, health_monitor: HealthMonitor = None):
        self.mcp = mcp_registry
        self.health = health_monitor or HealthMonitor()
        self.capabilities = {} # ex: {"publish_short_video": ["PinterestServer"]}
        
    def map_capability(self, capability_name: str, server_providers: list):
        self.capabilities[capability_name] = server_providers
        
    def execute_capability(self, capability_name: str, provider_preference: str = None, **kwargs):
        if capability_name not in self.capabilities:
            raise ValueError(f"Capacidade {capability_name} não suportada pelo sistema.")
            
        providers = self.capabilities[capability_name]
        
        # Escolha do provedor com Circuit Breaker
        target_provider = None
        
        # Tenta a preferência primeiro
        if provider_preference and provider_preference in providers:
            if self.health.check_provider(provider_preference):
                target_provider = provider_preference
                
        # Se não há preferência ou ela está down, faz o fallback
        if not target_provider:
            for provider in providers:
                if self.health.check_provider(provider):
                    target_provider = provider
                    break
                    
        if not target_provider:
            raise RuntimeError(f"Circuit Breaker Aberto: Nenhum provedor saudável para {capability_name}.")
        
        # Repassa para o barramento MCP real
        return self.mcp.route_call(target_provider, capability_name, **kwargs)
