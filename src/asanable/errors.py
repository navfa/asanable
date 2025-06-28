"""Domain-specific exceptions for asanable."""


class AsanableError(Exception):
    """Base exception for all asanable errors."""


class AsanaConnectionError(AsanableError):
    """Failed to connect to the Asana API."""


class AsanaAuthError(AsanableError):
    """Asana authentication failed (invalid or missing token)."""


class ConfigurationError(AsanableError):
    """Missing or invalid configuration."""
