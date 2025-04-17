"""Middleware management for the Forge framework.

This module provides the MiddlewareManager class for managing middleware components.
Middleware are components that process requests and responses before and after the
main route handler execution.
"""

from typing import Any, Callable, List, Protocol, TypeVar, Optional, AsyncIterable, Awaitable

T = TypeVar("T")


class Middleware:
    """Base class for middleware components.
    
    Middleware components can intercept and modify requests and responses
    during the request handling lifecycle.
    """
    
    async def process(self, request: Any, next: Callable[[Any], Awaitable[Any]]) -> Any:
        """Process a request and response.
        
        Args:
            request: The request to process.
            next: The next middleware or handler in the chain.
            
        Returns:
            The response after processing.
        """
        return await next(request)


class MiddlewareStack:
    """A stack of middleware components.
    
    This class manages a stack of middleware components and applies them in the correct order.
    """
    
    def __init__(self):
        """Initialize a new MiddlewareStack."""
        self.stack: List[Middleware] = []
    
    def add(self, middleware: Middleware) -> None:
        """Add a middleware component to the stack.
        
        Args:
            middleware: The middleware component to add.
        """
        self.stack.append(middleware)
    
    def remove(self, middleware: Middleware) -> None:
        """Remove a middleware component from the stack.
        
        Args:
            middleware: The middleware component to remove.
        """
        if middleware in self.stack:
            self.stack.remove(middleware)
    
    def insert(self, index: int, middleware: Middleware) -> None:
        """Insert a middleware component at a specific position in the stack.
        
        Args:
            index: The position to insert the middleware.
            middleware: The middleware component to insert.
        """
        self.stack.insert(index, middleware)
    
    async def process(self, request: Any, handler: Callable[[Any], Awaitable[Any]]) -> Any:
        """Process a request through all middleware in the stack.
        
        Args:
            request: The request to process.
            handler: The final handler for the request.
            
        Returns:
            The response after processing.
        """
        middleware_chain = self._create_middleware_chain(handler)
        return await middleware_chain(request)
    
    def _create_middleware_chain(self, handler: Callable[[Any], Awaitable[Any]]) -> Callable[[Any], Awaitable[Any]]:
        """Create a chain of middleware components.
        
        Args:
            handler: The final handler for the request.
            
        Returns:
            A function that applies all middleware and calls the handler.
        """
        async def final_handler(request: Any) -> Any:
            return await handler(request)
        
        chain = final_handler
        
        for middleware in reversed(self.stack):
            next_middleware = chain
            chain = lambda req, mid=middleware, next=next_middleware: mid.process(req, next)
        
        return chain


class RequestMiddleware(Protocol):
    """Protocol for request preprocessing middleware."""
    
    def process_request(self, request: Any) -> Any:
        """Process a request before it is handled by a route handler.
        
        Args:
            request: The request to process.
            
        Returns:
            The processed request, which may be modified.
        """
        ...


class ResponseMiddleware(Protocol):
    """Protocol for response postprocessing middleware."""
    
    def process_response(self, request: Any, response: Any) -> Any:
        """Process a response before it is returned to the client.
        
        Args:
            request: The original request.
            response: The response to process.
            
        Returns:
            The processed response, which may be modified.
        """
        ...


class ExceptionMiddleware(Protocol):
    """Protocol for exception handling middleware."""
    
    def process_exception(self, request: Any, exception: Exception) -> Any:
        """Process an exception raised during request handling.
        
        Args:
            request: The request that was being processed when the exception occurred.
            exception: The exception that was raised.
            
        Returns:
            A response to return to the client, typically an error response.
        """
        ...


class MiddlewareManager:
    """Manager for middleware components.
    
    This class manages middleware components and applies them in the correct order
    during request processing.
    """
    
    def __init__(self, app: Any) -> None:
        """Initialize a new MiddlewareManager.
        
        Args:
            app: The Forge application instance.
        """
        self._app = app
        self._request_middleware: List[RequestMiddleware] = []
        self._response_middleware: List[ResponseMiddleware] = []
        self._exception_middleware: List[ExceptionMiddleware] = []
        
        # Add the default error handling middleware
        self._default_error_handler = DefaultErrorHandlingMiddleware(app)
        self.add(self._default_error_handler)
    
    def add(self, middleware: Any) -> None:
        """Add a middleware component.
        
        This method adds a middleware component to the appropriate lists based on
        its implemented protocols.
        
        Args:
            middleware: The middleware component to add.
        """
        if hasattr(middleware, "process_request"):
            self._request_middleware.append(middleware)
        
        if hasattr(middleware, "process_response"):
            self._response_middleware.append(middleware)
        
        if hasattr(middleware, "process_exception"):
            self._exception_middleware.append(middleware)
    
    def process_request(self, request: Any) -> Any:
        """Process a request through all request middleware.
        
        Args:
            request: The request to process.
            
        Returns:
            The processed request.
        """
        processed_request = request
        for middleware in self._request_middleware:
            processed_request = middleware.process_request(processed_request)
        return processed_request
    
    def process_response(self, request: Any, response: Any) -> Any:
        """Process a response through all response middleware.
        
        Args:
            request: The original request.
            response: The response to process.
            
        Returns:
            The processed response.
        """
        processed_response = response
        for middleware in reversed(self._response_middleware):
            processed_response = middleware.process_response(request, processed_response)
        return processed_response
    
    def process_exception(self, request: Any, exception: Exception) -> Any:
        """Process an exception through all exception middleware.
        
        Args:
            request: The request that was being processed when the exception occurred.
            exception: The exception that was raised.
            
        Returns:
            A response to return to the client.
        """
        for middleware in self._exception_middleware:
            try:
                response = middleware.process_exception(request, exception)
                if response is not None:
                    return response
            except Exception:
                # If an exception middleware fails, continue to the next one
                continue
        
        # If no middleware handles the exception, re-raise it
        raise exception


class DefaultErrorHandlingMiddleware:
    """Default middleware for handling exceptions.
    
    This middleware provides basic error handling for common exception types.
    It is automatically added to all Forge applications.
    """
    
    def __init__(self, app: Any) -> None:
        """Initialize a new DefaultErrorHandlingMiddleware.
        
        Args:
            app: The Forge application instance.
        """
        self._app = app
    
    def process_exception(self, request: Any, exception: Exception) -> Optional[Any]:
        """Process an exception and generate an appropriate error response.
        
        Args:
            request: The request that was being processed when the exception occurred.
            exception: The exception that was raised.
            
        Returns:
            An error response.
        """
        try:
            # Import locally to avoid circular imports
            from forge_http import Response
            
            # Handle different types of exceptions
            if isinstance(exception, ValueError):
                # Bad request for value errors
                return Response.json(
                    {"error": str(exception)},
                    status=400,
                )
            elif isinstance(exception, PermissionError):
                # Forbidden for permission errors
                return Response.json(
                    {"error": "Permission denied"},
                    status=403,
                )
            elif isinstance(exception, FileNotFoundError):
                # Not found for missing files
                return Response.json(
                    {"error": "Resource not found"},
                    status=404,
                )
            else:
                # Internal server error for all other exceptions
                debug_mode = getattr(self._app.config, 'debug', False)
                if debug_mode:
                    # Include traceback in debug mode
                    import traceback
                    return Response.json(
                        {
                            "error": "Internal server error",
                            "exception": str(exception),
                            "traceback": traceback.format_exc(),
                        },
                        status=500,
                    )
                else:
                    # Hide details in production
                    return Response.json(
                        {"error": "Internal server error"},
                        status=500,
                    )
        except Exception:
            # If we can't create a proper response, return None
            # This will cause the exception to be re-raised
            return None 