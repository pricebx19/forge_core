"""Test utilities for Forge Core.

This module provides test utilities that make it easier to test
Forge Core components without dependencies on other packages.
"""

from typing import Any, Dict, List, Optional, TypeVar, Union
from forge_core.interfaces import IRequest, IResponse
from forge_http.headers import Headers

T = TypeVar('T')


class MockRequest:
    """Mock implementation of IRequest for testing."""
    
    def __init__(
        self,
        method: str = "GET",
        url: str = "/",
        path: str = "/",
        headers: Optional[Dict[str, str]] = None,
        body: bytes = b"",
        query_params: Optional[Dict[str, str]] = None
    ):
        """Initialize a mock request."""
        self._method = method
        self._url = url
        self._path = path
        self._headers = Headers(headers or {})
        self._body = body
        self._query_params = query_params or {}
        self.attributes = {}  # Used by middleware
    
    @property
    def method(self) -> str:
        """Get the HTTP method."""
        return self._method
    
    @property
    def url(self) -> str:
        """Get the request URL."""
        return self._url
    
    @property
    def path(self) -> str:
        """Get the request path."""
        return self._path
    
    @property
    def headers(self) -> Headers:
        """Get the request headers."""
        return self._headers
    
    @property
    def body(self) -> bytes:
        """Get the request body."""
        return self._body
    
    def param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter by name."""
        return self._query_params.get(name, default)


class MockResponse:
    """Mock implementation of IResponse for testing."""
    
    def __init__(
        self,
        body: bytes = b"",
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize a mock response."""
        self._body = body
        self._status = status
        self._headers = Headers(headers or {})
    
    @property
    def status(self) -> int:
        """Get the HTTP status code."""
        return self._status
    
    @property
    def headers(self) -> Headers:
        """Get the response headers."""
        return self._headers
    
    @property
    def body(self) -> bytes:
        """Get the response body."""
        return self._body
    
    @classmethod
    def text(cls, text: str, status: int = 200, headers: Optional[Dict[str, str]] = None) -> "MockResponse":
        """Create a text response."""
        # Create a Headers object with the initial headers
        all_headers = Headers(headers or {})
        all_headers.set("Content-Type", "text/plain; charset=utf-8")
        
        return cls(
            body=text.encode("utf-8"),
            status=status,
            headers=dict(all_headers.items()),  # Convert to dict for constructor
        )
    
    @classmethod
    def json(cls, data: Any, status: int = 200, headers: Optional[Dict[str, str]] = None) -> "MockResponse":
        """Create a JSON response."""
        import json
        # Create a Headers object with the initial headers
        all_headers = Headers(headers or {})
        all_headers.set("Content-Type", "application/json; charset=utf-8")
        
        return cls(
            body=json.dumps(data).encode("utf-8"),
            status=status,
            headers=dict(all_headers.items()),  # Convert to dict for constructor
        )
    
    @classmethod
    def redirect(cls, location: str, status: int = 302, headers: Optional[Dict[str, str]] = None) -> "MockResponse":
        """Create a redirect response."""
        # Create a Headers object with the initial headers
        all_headers = Headers(headers or {})
        all_headers.set("Location", location)
        
        return cls(
            body=b"",
            status=status,
            headers=dict(all_headers.items()),  # Convert to dict for constructor
        ) 