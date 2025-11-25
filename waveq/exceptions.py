"""
Custom exceptions for WaveQ SDK
"""


class WaveQException(Exception):
    """Base exception for all WaveQ errors"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(WaveQException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class ValidationError(WaveQException):
    """Raised when request validation fails"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, status_code=400)
        self.field = field


class ProcessingError(WaveQException):
    """Raised when audio processing fails"""
    
    def __init__(self, message: str, task_id: str = None):
        super().__init__(message, status_code=500)
        self.task_id = task_id


class ResourceNotFoundError(WaveQException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(WaveQException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class InvalidAudioFormatError(ValidationError):
    """Raised when audio format is not supported"""
    
    def __init__(self, format_provided: str, supported_formats: list = None):
        message = f"Invalid audio format: {format_provided}"
        if supported_formats:
            message += f". Supported formats: {', '.join(supported_formats)}"
        super().__init__(message, field="audio_file")
        self.format_provided = format_provided
        self.supported_formats = supported_formats
