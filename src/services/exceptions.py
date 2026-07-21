class RetryableError(Exception):
    def __init__(self, reason: str, message: str = ""):
        self.reason = reason
        super().__init__(message or reason)

class FatalError(Exception):
    def __init__(self, reason: str, message: str = ""):
        self.reason = reason
        super().__init__(message or reason)
