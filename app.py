"""Core application class for Forge framework.

This module provides the main App class that serves as the entry point for all Forge applications.
The App class manages the application lifecycle, dependency injection, and runtime configuration.
"""

from typing import Any, Dict, Optional, Protocol, TypeVar, List

from kink import Container

from forge_core.config import Config
from forge_core.lifecycle import LifecycleManager, LifecyclePhase
from forge_core.middleware import MiddlewareManager

T = TypeVar("T")


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


class App:
    """Main application class for Forge framework.
    
    This class serves as the entry point for all Forge applications. It manages the application
    lifecycle, dependency injection, and runtime configuration.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        container: Optional[Container] = None,
    ) -> None:
        """Initialize a new Forge application.
        
        Args:
            config: Optional configuration object. If not provided, default config is used.
            container: Optional dependency injection container. If not provided, a new one is created.
        """
        self._config = config or Config()
        self._container = container or Container()
        self._lifecycle = LifecycleManager(self)
        self._middleware = MiddlewareManager(self)
        # Import Kernel here to avoid circular dependency
        from forge_core.kernel import Kernel
        self._kernel = Kernel(self)
        self._routers = []

    @classmethod
    def create(cls, **kwargs: Any) -> "App":
        """Create a new Forge application instance.
        
        This is the preferred way to create a new Forge application. It ensures proper
        initialization and setup of all required components.
        
        Args:
            **kwargs: Additional arguments to pass to the App constructor.
            
        Returns:
            A new App instance.
        """
        return cls(**kwargs)

    def run(self) -> None:
        """Run the Forge application.
        
        This method starts the application lifecycle and begins processing requests.
        It should be called after all configuration and setup is complete.
        """
        self._lifecycle.start()
        self._kernel.run()

    def stop(self) -> None:
        """Stop the Forge application.
        
        This method gracefully shuts down the application, ensuring all resources
        are properly cleaned up.
        """
        self._lifecycle.stop()
        self._kernel.stop()
    
    def register_router(self, router: IRouter) -> None:
        """Register a router with the application.
        
        This method registers a router with the application, making its routes
        available for request handling.
        
        Args:
            router: The router to register.
        """
        self._routers.append(router)
        
        # Apply router middleware to the application
        for middleware in router.middleware:
            self._middleware.add(middleware)
        
        # Register the router with the kernel for route matching
        self._kernel.register_router(router)
        
    def route(self, path: str, methods=None):
        """Register a route with the application.
        
        This is a decorator that registers a function as a route handler.
        
        Args:
            path: The URL path to match.
            methods: HTTP methods to match. Defaults to ["GET"].
            
        Returns:
            A decorator function that registers the handler.
        """
        methods = methods or ["GET"]
        
        def decorator(func):
            # Create a route object
            route = {
                "path": path,
                "methods": methods,
                "handler": func
            }
            
            # In a real implementation, we would add this to a router
            # For testing purposes, we'll add a match method to the route
            def match(path_to_match, method_to_match):
                # Simple path parameter handling
                if "{" in path and "}" in path:
                    # Extract path params from the pattern
                    path_parts = path.split("/")
                    check_parts = path_to_match.split("/")
                    
                    # Check if path structures match
                    if len(path_parts) != len(check_parts):
                        raise ValueError("Route not found")
                    
                    params = {}
                    for i, part in enumerate(path_parts):
                        if part.startswith("{") and part.endswith("}"):
                            # Extract parameter name
                            param_name = part[1:-1]
                            params[param_name] = check_parts[i]
                        elif part != check_parts[i]:
                            raise ValueError("Route not found")
                    
                    if method_to_match in methods:
                        return route, params
                elif path_to_match == path and method_to_match in methods:
                    return route, {}
                
                raise ValueError("Route not found")
            
            route["match"] = match
            
            # Add the route to the kernel
            class SimpleRouter:
                @property
                def routes(self):
                    return [route]
                
                @property
                def middleware(self):
                    return []
                
                def match(self, path_to_match, method_to_match):
                    return route.get("match")(path_to_match, method_to_match)
            
            self.register_router(SimpleRouter())
            
            return func
        
        return decorator

    def middleware(self, func=None):
        """Register a middleware function with the application.
        
        This method is a decorator for middleware functions. It creates a middleware
        class that wraps the decorated function and adds it to the middleware stack.
        
        Args:
            func: The middleware function to register.
            
        Returns:
            The middleware function.
        """
        # Support both @app.middleware and @app.middleware() syntax
        if func is None:
            # Called as @app.middleware()
            def decorator(inner_func):
                class FunctionMiddleware:
                    async def process(self, request, next):
                        return await inner_func(request, next)
                self._middleware.add(FunctionMiddleware())
                return inner_func
            return decorator
        else:
            # Called as @app.middleware
            class FunctionMiddleware:
                async def process(self, request, next):
                    return await func(request, next)
            self._middleware.add(FunctionMiddleware())
            return func

    def on_error(self, exception_type):
        """Register an error handler for a specific exception type.
        
        This is a decorator that registers a function as an error handler.
        
        Args:
            exception_type: The exception type to handle.
            
        Returns:
            A decorator function that registers the handler.
        """
        def decorator(func):
            # Register the function with the lifecycle manager
            @self._lifecycle.on(LifecyclePhase.ERROR)
            async def handle_error(error, request):
                if isinstance(error, exception_type):
                    return await func(error, request)
                return None
            
            return func
        
        return decorator

    @property
    def config(self) -> Config:
        """Get the application configuration."""
        return self._config

    @property
    def container(self) -> Container:
        """Get the dependency injection container."""
        return self._container

    @property
    def lifecycle(self) -> LifecycleManager:
        """Get the lifecycle manager."""
        return self._lifecycle

    @property
    def middleware(self) -> MiddlewareManager:
        """Get the middleware manager."""
        return self._middleware

    @property
    def kernel(self):
        """Get the HTTP kernel."""
        return self._kernel

    @property
    def routes(self):
        """Get all registered routes."""
        all_routes = []
        for router in self._routers:
            all_routes.extend(router.routes)
        return [route["path"] for route in all_routes if isinstance(route, dict) and "path" in route]

    async def handle(self, request):
        """Handle a request.
        
        This is a shortcut method that forwards the request to the kernel.
        
        Args:
            request: The request to handle.
            
        Returns:
            The response.
        """
        return await self._kernel.handle(request)
        
    def handle_request(self, request):
        """Handle a request synchronously.
        
        This is a shortcut method for tests that need a synchronous interface.
        
        Args:
            request: The request to handle.
            
        Returns:
            The response.
        """
        import asyncio
        return asyncio.run(self.handle(request))

# Add alias for backward compatibility
ForgeApplication = App 