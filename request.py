"""HTTP request handling for Forge framework.

This module provides the Request class that represents HTTP requests,
including headers, body, and query parameters.
"""

import json
from typing import Any, Dict, Optional, TypeVar, Union, MutableMapping
from urllib.parse import parse_qs

import orjson
from multidict import MultiDict

T = TypeVar("T")


class RequestParsingError(Exception):
    """Exception raised when a request body cannot be parsed."""
    pass


class Request:
    """HTTP request for Forge applications.
    
    This class represents an HTTP request, including headers, body,
    and query parameters.
    """

    def __init__(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        query_params: Optional[Dict[str, str]] = None,
        path_params: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize a new HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            url: Request URL.
            headers: HTTP headers.
            body: Request body.
            query_params: Query parameters from URL.
            path_params: Path parameters from URL.
        """
        self.method = method.upper()
        self.url = url
        self.headers = headers or {}
        self.body = body or b""
        self.query_params = query_params or {}
        self.path_params = path_params or {}
        self.attributes: Dict[str, Any] = {}
        self._json: Optional[Any] = None
        self._form: Optional[Dict[str, str]] = None

    @property
    def content_type(self) -> str:
        """Get the content type of the request."""
        content_type = self.headers.get("Content-Type", "")
        if ";" in content_type:
            return content_type.split(";")[0].strip()
        return content_type

    def parsed_body(self) -> Dict[str, Any]:
        """Parse the request body based on content type.
        
        Returns:
            Dict containing the parsed body
            
        Raises:
            RequestParsingError: If the body cannot be parsed according to the content type
        """
        if not self.body:
            return {}
            
        content_type = self.content_type.lower()
        
        try:
            if content_type == "application/json":
                return json.loads(self.body.decode("utf-8"))
                
            elif content_type == "application/x-www-form-urlencoded":
                parsed = parse_qs(self.body.decode("utf-8"))
                # Convert lists to single values for simple form data
                return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                
            elif content_type.startswith("multipart/form-data"):
                # Simplified multipart handling - for more complex handling, use a dedicated library
                raise NotImplementedError("Multipart form data parsing is not implemented")
                
            else:
                # For unknown content types, return the raw body
                return {"body": self.body.decode("utf-8")}
                
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise RequestParsingError(f"Failed to parse request body: {str(e)}") from e
            
    def json(self) -> Dict[str, Any]:
        """Parse the request body as JSON.
        
        Returns:
            Dict containing the parsed JSON
            
        Raises:
            RequestParsingError: If the body is not valid JSON
        """
        if not self.body:
            return {}
            
        try:
            return json.loads(self.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise RequestParsingError(f"Failed to parse JSON body: {str(e)}") from e
            
    def form(self) -> Dict[str, Any]:
        """Parse the request body as form data.
        
        Returns:
            Dict containing the parsed form data
            
        Raises:
            RequestParsingError: If the body cannot be parsed as form data
        """
        if not self.body:
            return {}
            
        try:
            parsed = parse_qs(self.body.decode("utf-8"))
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except UnicodeDecodeError as e:
            raise RequestParsingError(f"Failed to parse form data: {str(e)}") from e

    @property
    def path(self) -> str:
        """Get request path."""
        return self.url

    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a header value.
        
        Args:
            name: Header name.
            default: Default value if header is not set.
            
        Returns:
            Header value or default.
        """
        return self.headers.get(name, default)

    def get_query(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a query parameter value.
        
        Args:
            name: Parameter name.
            default: Default value if parameter is not set.
            
        Returns:
            Parameter value or default.
        """
        return self.query_params.get(name, default)

    def get_path_param(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a path parameter value.
        
        Args:
            name: Parameter name.
            default: Default value if parameter is not set.
            
        Returns:
            Parameter value or default.
        """
        return self.path_params.get(name, default)

    def get_attribute(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get an attribute value.
        
        Args:
            name: Attribute name.
            default: Default value if attribute is not set.
            
        Returns:
            Attribute value or default.
        """
        return self.attributes.get(name, default)

    def set_attribute(self, name: str, value: Any) -> None:
        """Set an attribute value.
        
        Args:
            name: Attribute name.
            value: Attribute value.
        """
        self.attributes[name] = value 