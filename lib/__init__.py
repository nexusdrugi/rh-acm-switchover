"""
Library package for ACM switchover automation.
"""

from .kube_client import KubeClient
from .exceptions import (
    SwitchoverError,
    TransientError,
    FatalError,
    ValidationError,
    ConfigurationError,
)
from .utils import (
    Phase,
    StateManager,
    setup_logging,
    parse_acm_version,
    is_acm_version_ge,
    format_duration,
    confirm_action,
)

__all__ = [
    "KubeClient",
    "SwitchoverError",
    "TransientError",
    "FatalError",
    "ValidationError",
    "ConfigurationError",
    "Phase",
    "StateManager",
    "setup_logging",
    "parse_acm_version",
    "is_acm_version_ge",
    "format_duration",
    "confirm_action",
]
