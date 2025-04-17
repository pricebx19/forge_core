"""HTTP response representation for Forge applications."""

import json
from typing import Any, Dict, Optional, Union, List


class ResponseError(Exception):
    """Exception raised for errors related to response creation."""
    pass


class Response:
    """Represents an HTTP response."""
    
    def __init__(
        self,
        content: Union[str, bytes] = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize a new response.
        
        Args:
            content: Response body
            status_code: HTTP status code
            headers: HTTP headers
            
        Raises:
            ResponseError: If the status code is invalid
        """
        if not isinstance(status_code, int) or status_code < 100 or status_code > 599:
            raise ResponseError(f"Invalid status code: {status_code}")
            
        self.status_code = status_code
        self.headers = headers or {}
        
        # Ensure content is bytes
        if isinstance(content, str):
            self.content = content.encode("utf-8")
        else:
            self.content = content

    @classmethod
    def text(cls, content: str, status_code: int = 200) -> "Response":
        """Create a text response.
        
        Args:
            content: Text content
            status_code: HTTP status code
            
        Returns:
            Response instance
        """
        headers = {"Content-Type": "text/plain; charset=utf-8"}
        return cls(content=content, status_code=status_code, headers=headers)

    @classmethod
    def html(cls, content: str, status_code: int = 200) -> "Response":
        """Create an HTML response.
        
        Args:
            content: HTML content
            status_code: HTTP status code
            
        Returns:
            Response instance
        """
        headers = {"Content-Type": "text/html; charset=utf-8"}
        return cls(content=content, status_code=status_code, headers=headers)

    @classmethod
    def json(cls, data: Any, status_code: int = 200) -> "Response":
        """Create a JSON response.
        
        Args:
            data: Data to serialize to JSON
            status_code: HTTP status code
            
        Returns:
            Response instance
            
        Raises:
            ResponseError: If data cannot be serialized to JSON
        """
        headers = {"Content-Type": "application/json"}
        try:
            content = json.dumps(data).encode("utf-8")
            return cls(content=content, status_code=status_code, headers=headers)
        except (TypeError, ValueError) as e:
            raise ResponseError(f"Failed to serialize data to JSON: {str(e)}") from e

    @classmethod
    def redirect(cls, location: str, permanent: bool = False) -> "Response":
        """Create a redirect response.
        
        Args:
            location: URL to redirect to
            permanent: Whether this is a permanent redirect
            
        Returns:
            Response instance
        """
        status_code = 301 if permanent else 302
        headers = {"Location": location}
        return cls(content="", status_code=status_code, headers=headers)

    @classmethod
    def not_found(cls, message: str = "Not Found") -> "Response":
        """Create a 404 Not Found response.
        
        Args:
            message: Error message
            
        Returns:
            Response instance
        """
        return cls.text(message, status_code=404)

    @classmethod
    def bad_request(cls, message: str = "Bad Request") -> "Response":
        """Create a 400 Bad Request response.
        
        Args:
            message: Error message
            
        Returns:
            Response instance
        """
        return cls.text(message, status_code=400)

    @classmethod
    def server_error(cls, message: str = "Internal Server Error") -> "Response":
        """Create a 500 Internal Server Error response.
        
        Args:
            message: Error message
            
        Returns:
            Response instance
        """
        return cls.text(message, status_code=500)

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> "Response":
        """Create a 401 Unauthorized response.
        
        Args:
            message: Error message
            
        Returns:
            Response instance
        """
        return cls.text(message, status_code=401)

    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> "Response":
        """Create a 403 Forbidden response.
        
        Args:
            message: Error message
            
        Returns:
            Response instance
        """
        return cls.text(message, status_code=403)

    def with_header(self, name: str, value: str) -> "Response":
        """Add or update a header in the response.
        
        Args:
            name: Header name
            value: Header value
            
        Returns:
            Self for method chaining
        """
        self.headers[name] = value
        return self

    def with_status(self, status_code: int) -> "Response":
        """Change the status code of the response.
        
        Args:
            status_code: New HTTP status code
            
        Returns:
            Self for method chaining
            
        Raises:
            ResponseError: If the status code is invalid
        """
        if not isinstance(status_code, int) or status_code < 100 or status_code > 599:
            raise ResponseError(f"Invalid status code: {status_code}")
            
        self.status_code = status_code
        return self 