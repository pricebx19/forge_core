"""Forge Core - The heart of the Forge framework.

This package provides the core functionality for the Forge framework,
including the application runtime, request lifecycle, HTTP kernel,
and dependency injection container.
"""

# Define version
__version__ = "0.1.0"

# Import public API
# Note: Import objects at usage time to avoid circular imports
__all__ = [
    "App",
    "ForgeApplication",
    "Config",
    "Kernel",
    "LifecycleListener",
    "LifecycleManager",
    "Middleware",
    "MiddlewareManager",
    "Request",
    "Response",
]

# Import these directly since they don't have circular dependencies
from forge_core.config import Config
from forge_core.request import Request
from forge_core.response import Response 