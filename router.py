"""Router implementation for Forge framework.

This module provides router classes for the Forge framework.
Routers are responsible for matching requests to handlers.
"""

from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union

from forge_core.interfaces import IRequest, IResponse


class IRouter(Protocol):
    """Protocol for router components."""
    
    @property
    def routes(self) -> List[Any]:
        """Get all routes registered with this router."""
        ...
    
    @property
    def middleware(self) -> List[Any]:
        """Get middleware applied to all routes in this router."""
        ...
    
    def match(self, path: str, method: str) -> Tuple[Any, Dict[str, str]]:
        """Match a request path and method to a route.
        
        Args:
            path: The request path.
            method: The request method.
            
        Returns:
            A tuple containing the matched route and any path parameters.
            
        Raises:
            ValueError: If no route matches.
        """
        ...


class SimpleRouter:
    """A simple router implementation for testing.
    
    This router supports basic path matching and path parameters.
    """
    
    def __init__(self):
        """Initialize a new SimpleRouter."""
        self._routes = []
        self._middlewares = []
    
    @property
    def routes(self) -> List[Any]:
        """Get all routes registered with this router."""
        return self._routes
    
    @property
    def middleware(self) -> List[Any]:
        """Get middleware applied to all routes in this router."""
        return self._middlewares
    
    def add_middleware(self, middleware: Any) -> None:
        """Add middleware to the router.
        
        Args:
            middleware: The middleware to add.
        """
        self._middlewares.append(middleware)
    
    def add_route(self, path: str, handler: Callable, methods: List[str] = None) -> None:
        """Add a route to the router.
        
        Args:
            path: The URL path pattern.
            handler: The handler function.
            methods: The HTTP methods to match. Defaults to ["GET"].
        """
        methods = methods or ["GET"]
        route = {
            "path": path,
            "methods": methods,
            "handler": handler
        }
        self._routes.append(route)
    
    def match(self, path: str, method: str) -> Tuple[Any, Dict[str, str]]:
        """Match a request path and method to a route.
        
        Args:
            path: The request path.
            method: The request method.
            
        Returns:
            A tuple containing the matched route and any path parameters.
            
        Raises:
            ValueError: If no route matches.
        """
        for route in self._routes:
            route_path = route["path"]
            route_methods = route["methods"]
            
            # Skip if method doesn't match
            if method not in route_methods:
                continue
            
            # Simple path parameter handling
            if "{" in route_path and "}" in route_path:
                # Extract path params from the pattern
                path_parts = route_path.split("/")
                check_parts = path.split("/")
                
                # Check if path structures match
                if len(path_parts) != len(check_parts):
                    continue
                
                params = {}
                match = True
                
                for i, part in enumerate(path_parts):
                    if part.startswith("{") and part.endswith("}"):
                        # Extract parameter name
                        param_name = part[1:-1]
                        params[param_name] = check_parts[i]
                    elif part != check_parts[i]:
                        match = False
                        break
                
                if match:
                    return route, params
            elif path == route_path:
                return route, {}
        
        raise ValueError(f"No route found for {method} {path}") 