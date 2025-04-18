"""HTTP service for the Forge framework.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the forge_http.HttpService class instead.

This module provides a service for handling HTTP requests. It leverages
the RouteService from forge_router to handle route matching and implements
the business logic for processing HTTP requests.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

try:
    from forge_router import RouteService, HandlerNotFound
except ImportError:
    # For backward compatibility
    from forge_core.router_bridge import RouterBridge as RouteService
    # Define a mock HandlerNotFound for backward compatibility
    class HandlerNotFound(Exception):
        pass

from forge_core.interfaces import IRequest, IResponse
from forge_core.services import BaseService
from forge_core.test_utils import MockResponse


class HttpService(BaseService):
    """Service for handling HTTP requests.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_http.HttpService class instead.
    
    This service handles HTTP requests, including route matching, handler
    execution, and error handling.
    """
    
    def __init__(self, app: Any = None) -> None:
        """Initialize a new HttpService.
        
        Args:
            app: The forge application instance.
        """
        super().__init__(getattr(app, "container", None))
        self._app = app
        self._route_service = RouteService()
        
        # If app has routers, register them with the route service
        if hasattr(app, "_routers"):
            for router in app._routers:
                self._route_service.register_router(router)
    
    def register_router(self, router: Any) -> None:
        """Register a router with the HTTP service.
        
        Args:
            router: The router to register.
        """
        self._route_service.register_router(router)
    
    async def handle_request(self, request: IRequest) -> IResponse:
        """Handle an HTTP request.
        
        Args:
            request: The HTTP request to handle.
            
        Returns:
            The HTTP response.
        """
        try:
            # Get the handler for the request
            handler = self._route_service.create_handler_with_params(request)
            
            # Execute the handler
            return await handler(request)
        except HandlerNotFound:
            # If no handler is found, return a 404 response
            return self._create_not_found_response(request)
        except Exception as e:
            # If an error occurs, return a 500 response
            return self._handle_error(e)
    
    def _create_not_found_response(self, request: IRequest) -> IResponse:
        """Create a 404 Not Found response.
        
        Args:
            request: The HTTP request that could not be matched.
            
        Returns:
            A 404 Not Found response.
        """
        # Use app's not found handler if available
        if hasattr(self._app, "handle_not_found"):
            return self._app.handle_not_found(request)
        
        # Create a default 404 response
        return MockResponse(
            status=404,
            body=b"Not Found",
            headers={"Content-Type": "text/plain"},
        )
    
    def _handle_error(self, error: Exception) -> IResponse:
        """Handle an error by returning an appropriate error response.
        
        Args:
            error: The exception that was raised.
            
        Returns:
            An error response.
        """
        # Use app's error handler if available
        if hasattr(self._app, "handle_error"):
            return self._app.handle_error(error)
        
        # Log the error for debugging
        print(f"Error handling request: {error}")
        
        # Create a default error response
        import json
        if hasattr(error, "status_code"):
            status_code = error.status_code
        else:
            status_code = 500
            
        return MockResponse(
            body=json.dumps({"error": str(error)}).encode(),
            status=status_code,
            headers={"Content-Type": "application/json"}
        ) 