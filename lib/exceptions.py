"""
Custom exceptions for ACM switchover automation.
"""


class SwitchoverError(Exception):
    """Base class for all switchover errors."""

    pass


class TransientError(SwitchoverError):
    """
    Error that might be resolved by retrying.
    Examples: Network timeouts, 503 Service Unavailable.
    """

    pass


class FatalError(SwitchoverError):
    """
    Error that cannot be resolved by retrying.
    Examples: Invalid configuration, missing permissions, 404 Not Found (when expected).
    """

    pass


class ValidationError(FatalError):
    """Pre-flight validation failure."""

    pass


class ConfigurationError(FatalError):
    """Invalid configuration or arguments."""

    pass
