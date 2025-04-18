"""Error handling service for the Forge framework.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the forge_errors.ErrorService class instead.

This module provides a service for handling errors in the application.
It centralizes error handling logic and provides a consistent way to
handle errors across the application.
"""

import json
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, Union

from forge_core.services import BaseService
from forge_core.interfaces import IRequest, IResponse
from forge_core.test_utils import MockResponse
from forge_http import Response


class ErrorHandler:
    """Handler for specific error types.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_errors.ErrorHandler class instead.
    
    This class represents a handler for a specific error type. It is
    registered with the ErrorService to handle errors of that type.
    """
    
    def __init__(
        self,
        error_type: Type[Exception],
        handler: Callable[[Exception, Optional[IRequest]], IResponse],
        priority: int = 0
    ) -> None:
        """Initialize a new ErrorHandler.
        
        Args:
            error_type: The type of error this handler handles.
            handler: The function to call when an error of this type is encountered.
            priority: The priority of this handler. Higher priority handlers
                      are invoked first.
        """
        self.error_type = error_type
        self.handler = handler
        self.priority = priority
    
    def can_handle(self, error: Exception) -> bool:
        """Check if this handler can handle the given error.
        
        Args:
            error: The error to check.
            
        Returns:
            True if this handler can handle the error.
        """
        return isinstance(error, self.error_type)
    
    async def handle(self, error: Exception, request: Optional[IRequest] = None) -> IResponse:
        """Handle the error.
        
        Args:
            error: The error to handle.
            request: The request associated with the error.
            
        Returns:
            The response to return.
        """
        return await self.handler(error, request)


class ErrorService(BaseService):
    """Service for handling errors in the application.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_errors.ErrorService class instead.
    
    This service centralizes error handling logic and provides a consistent
    way to handle errors across the application.
    """
    
    def __init__(self, container=None) -> None:
        """Initialize a new ErrorService.
        
        Args:
            container: Optional dependency injection container.
        """
        super().__init__(container)
        self._handlers: List[ErrorHandler] = []
        
        # Register default handlers
        self.register(Exception, self._default_handler)
    
    def register(
        self,
        error_type: Type[Exception],
        handler: Callable[[Exception, Optional[IRequest]], IResponse],
        priority: int = 0
    ) -> ErrorHandler:
        """Register a handler for a specific error type.
        
        Args:
            error_type: The type of error to handle.
            handler: The function to call when an error of this type is encountered.
            priority: The priority of this handler. Higher priority handlers
                     are invoked first.
                     
        Returns:
            The error handler that was created.
        """
        handler_obj = ErrorHandler(error_type, handler, priority)
        self._handlers.append(handler_obj)
        
        # Sort handlers by priority (highest first)
        self._handlers.sort(key=lambda h: -h.priority)
        
        return handler_obj
    
    def unregister(self, handler: ErrorHandler) -> bool:
        """Unregister an error handler.
        
        Args:
            handler: The error handler to unregister.
            
        Returns:
            True if the handler was removed, False otherwise.
        """
        if handler not in self._handlers:
            return False
        
        self._handlers.remove(handler)
        return True
    
    async def handle(self, error: Exception, request: Optional[IRequest] = None) -> IResponse:
        """Handle an error.
        
        This method finds the appropriate handler for the error and invokes it.
        
        Args:
            error: The error to handle.
            request: The request associated with the error.
            
        Returns:
            The response to return.
        """
        for handler in self._handlers:
            if handler.can_handle(error):
                return await handler.handle(error, request)
        
        # If no handler is found, use the default handler
        return await self._default_handler(error, request)
    
    async def _default_handler(self, error: Exception, request: Optional[IRequest] = None) -> IResponse:
        """Default handler for errors.
        
        This handler is used when no other handler is found for an error.
        
        Args:
            error: The error to handle.
            request: The request associated with the error.
            
        Returns:
            A default error response.
        """
        # Log the error for debugging
        print(f"Error: {error}")
        traceback.print_exception(type(error), error, error.__traceback__)
        
        # Create a default error response
        if hasattr(error, "status_code"):
            status_code = error.status_code
        else:
            status_code = 500
        
        error_data = {
            "error": str(error),
            "type": error.__class__.__name__
        }
        
        # Add traceback in development mode
        if request and hasattr(request, "app") and hasattr(request.app, "config"):
            if request.app.config.debug:
                error_data["traceback"] = traceback.format_exception(
                    type(error), error, error.__traceback__
                )
        
        return MockResponse(
            body=json.dumps(error_data).encode(),
            status=status_code,
            headers={"Content-Type": "application/json"}
        ) 