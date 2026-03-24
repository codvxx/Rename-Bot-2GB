class AppError(Exception):
    """Base application exception."""


class ConfigError(AppError):
    """Raised when environment configuration is invalid."""


class ValidationError(AppError):
    """Raised when user or input validation fails."""


class AccessError(AppError):
    """Raised when a user attempts an unauthorized action."""


class MediaProcessingError(AppError):
    """Raised when media processing fails."""
