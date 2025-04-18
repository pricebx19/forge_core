"""Interfaces for the Forge Core framework.

This module defines the core interfaces/protocols that Forge components implement.
These interfaces enable loose coupling between components and make testing easier.
"""

from typing import Any, Dict, List, Protocol, TypeVar, Union, Optional
from forge_http.headers import Headers

T = TypeVar('T')


class IRequest(Protocol):
    """Protocol defining the interface for HTTP requests."""
    
    @property
    def method(self) -> str:
        """Get the HTTP method."""
        ...
    
    @property
    def url(self) -> str:
        """Get the request URL."""
        ...
    
    @property
    def path(self) -> str:
        """Get the request path."""
        ...
    
    @property
    def headers(self) -> Headers:
        """Get the request headers."""
        ...
    
    @property
    def body(self) -> bytes:
        """Get the request body."""
        ...
    
    def param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter by name."""
        ...


class IResponse(Protocol):
    """Protocol defining the interface for HTTP responses."""
    
    @property
    def status(self) -> int:
        """Get the HTTP status code."""
        ...
    
    @property
    def headers(self) -> Headers:
        """Get the response headers."""
        ...
    
    @property
    def body(self) -> bytes:
        """Get the response body."""
        ...
    
    @classmethod
    def text(cls, text: str, status: int = 200, headers: Optional[Dict[str, str]] = None) -> 'IResponse':
        """Create a text response."""
        ...
    
    @classmethod
    def json(cls, data: Any, status: int = 200, headers: Optional[Dict[str, str]] = None) -> 'IResponse':
        """Create a JSON response."""
        ...
    
    @classmethod
    def redirect(cls, location: str, status: int = 302, headers: Optional[Dict[str, str]] = None) -> 'IResponse':
        """Create a redirect response."""
        ... 