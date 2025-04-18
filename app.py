"""Core application class for Forge framework.

This module provides the main App class that serves as the entry point for all Forge applications.
The App class manages the application lifecycle, dependency injection, and runtime configuration.
"""

from typing import Any, Dict, Optional, TypeVar, List, Callable

from kink import Container

from forge_core.config import Config
from forge_core.lifecycle import LifecycleManager, LifecyclePhase
from forge_core.middleware import MiddlewareManager
from forge_core.router import IRouter, SimpleRouter
# Import from forge_router package
try:
    from forge_router import RouterBridge, create_router
except ImportError:
    # For backward compatibility
    from forge_core.router_bridge import RouterBridge, create_router
from forge_core.services import ServiceRegistry
from forge_core.interfaces import IRequest, IResponse

# Import from forge_events package
try:
    from forge_events import EventService
except ImportError:
    # For backward compatibility
    from forge_core.event_service import EventService

# Import from forge_errors package
try:
    from forge_errors import ErrorService
except ImportError:
    # For backward compatibility
    from forge_core.error_service import ErrorService

# Import HTTP components from forge_http
try:
    from forge_http import Request, Response, HttpService
except ImportError:
    # For backward compatibility
    from forge_http import Request, Response
    from forge_core.http_service import HttpService

T = TypeVar("T")


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
        # Initialize core components
        self._config = config or Config()
        self._container = container or Container()
        self._services = ServiceRegistry(self._container)
        self._lifecycle = LifecycleManager(self)
        self._middleware = MiddlewareManager(self)
        
        # Register the app itself with the container
        self._container[App] = self
        
        # Initialize core services
        self._event_service = EventService(self._container)
        self._services.register("events", self._event_service)
        
        self._error_service = ErrorService(self._container)
        self._services.register("errors", self._error_service)
        
        # Import components here to avoid circular dependency
        from forge_core.kernel import Kernel
        
        # Initialize kernel and other components
        self._kernel = Kernel(self)
        self._routers = []
        
        # Create a default router using the bridge for improved compatibility
        self._default_router = create_router()
        self.register_router(self._default_router)
        
        # Register core services
        self._http_service = HttpService(self)
        self._services.register("http", self._http_service)

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
        # Publish application.starting event
        import asyncio
        asyncio.run(self._event_service.publish("application.starting", self))
        
        self._lifecycle.start()
        self._kernel.run()

    def stop(self) -> None:
        """Stop the Forge application.
        
        This method gracefully shuts down the application, ensuring all resources
        are properly cleaned up.
        """
        # Publish application.stopping event
        import asyncio
        asyncio.run(self._event_service.publish("application.stopping", self))
        
        self._lifecycle.stop()
        self._kernel.stop()
        
        # Publish application.stopped event
        asyncio.run(self._event_service.publish("application.stopped", self))
    
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
            self._default_router.add_route(path, func, methods)
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
            # Register with both the error service and the lifecycle error hooks
            self._error_service.register(exception_type, func)
            
            # For backward compatibility, also register with lifecycle
            @self._lifecycle.on(LifecyclePhase.ERROR)
            async def handle_error(error, request):
                if isinstance(error, exception_type):
                    return await func(error, request)
                return None
            
            return func
        
        return decorator
    
    async def handle_error(self, error: Exception, request: Optional[IRequest] = None) -> IResponse:
        """Handle an error.
        
        Args:
            error: The error to handle.
            request: The request associated with the error.
            
        Returns:
            The response to return.
        """
        return await self._error_service.handle(error, request)
    
    def on_event(self, event_name: str, priority: int = 0):
        """Register an event subscriber.
        
        This is a decorator that registers a function as an event subscriber.
        
        Args:
            event_name: The name of the event.
            priority: The priority of the subscriber. Higher priority subscribers
                    are invoked first.
            
        Returns:
            A decorator function that registers the subscriber.
        """
        def decorator(func):
            self._event_service.subscribe(event_name, func, priority)
            return func
        
        return decorator
    
    async def publish_event(self, event_name: str, event_data: Any = None) -> None:
        """Publish an event.
        
        Args:
            event_name: The name of the event.
            event_data: Optional data associated with the event.
        """
        await self._event_service.publish(event_name, event_data)
    
    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the application.
        
        Args:
            name: The name of the service.
            service: The service instance.
        """
        self._services.register(name, service)
    
    def get_service(self, name: str) -> Any:
        """Get a service by name.
        
        Args:
            name: The name of the service.
            
        Returns:
            The service instance.
            
        Raises:
            KeyError: If no service with the given name is registered.
        """
        return self._services.get(name)

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
    def services(self) -> ServiceRegistry:
        """Get the service registry."""
        return self._services
    
    @property
    def events(self) -> EventService:
        """Get the event service."""
        return self._event_service
    
    @property
    def errors(self) -> ErrorService:
        """Get the error service."""
        return self._error_service

    @property
    def routes(self):
        """Get all registered routes."""
        all_routes = []
        for router in self._routers:
            routes = router.routes
            for route in routes:
                # Handle both old-style dict routes and new IRoute objects
                if isinstance(route, dict) and "path" in route:
                    all_routes.append(route["path"])
                elif hasattr(route, "path"):
                    all_routes.append(route.path)
        return all_routes

    async def handle(self, request):
        """Handle a request.
        
        This is a shortcut method that forwards the request to the kernel.
        
        Args:
            request: The request to handle.
            
        Returns:
            The response.
        """
        try:
            # Publish request.received event
            await self._event_service.publish("request.received", request)
            
            # Handle the request
            response = await self._kernel.handle(request)
            
            # Publish request.completed event
            await self._event_service.publish("request.completed", {
                "request": request,
                "response": response
            })
            
            return response
        except Exception as e:
            # Publish request.error event
            await self._event_service.publish("request.error", {
                "request": request,
                "error": e
            })
            
            # Handle the error
            return await self._error_service.handle(e, request)
        
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