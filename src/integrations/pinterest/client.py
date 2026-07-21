"""
Facade temporário para garantir retrocompatibilidade enquanto o sistema transita
para a nova Reality Acquisition Layer.
"""
import warnings

warnings.warn(
    "src.integrations.pinterest está obsoleto. Use src.reality.social.pinterest",
    DeprecationWarning,
    stacklevel=2
)

from src.reality.social.pinterest.client import PinterestClient
from src.reality.social.pinterest.auth import PinterestAuth
from src.reality.social.pinterest.errors import PinterestError, PinterestAuthError
from src.reality.social.pinterest.rate_limit import RateLimitManager
from src.reality.social.pinterest.uploader import VideoUploader
from src.reality.social.pinterest.analytics import AnalyticsManager

__all__ = [
    "PinterestClient",
    "PinterestAuth",
    "PinterestError",
    "PinterestAuthError",
    "RateLimitManager",
    "VideoUploader",
    "AnalyticsManager"
]



