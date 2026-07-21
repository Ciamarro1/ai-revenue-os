class PinterestError(Exception):
    """Classe base para todas as exceções do Pinterest."""
    pass

class PinterestAuthError(PinterestError):
    """Exceção para falhas de autenticação ou token expirado."""
    pass

class PinterestRateLimitError(PinterestError):
    """Exceção para erro de limite de requisições excedido (HTTP 429)."""
    pass

class PinterestUploadError(PinterestError):
    """Exceção para falhas no fluxo de upload de mídia."""
    pass

class UploadTimeoutError(PinterestUploadError):
    """Exceção disparada quando o polling do upload de vídeo excede o tempo limite."""
    pass
