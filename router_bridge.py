"""Router bridge for migration from forge_core to forge_router.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the forge_router.bridge module instead.

This module provides bridge classes that make it easier to migrate from
the deprecated SimpleRouter in forge_core to the more robust Router in forge_router.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

try:
    from forge_router import Router as ForgeRouter, RouteService, RouteNotFoundException
    from forge_router.interfaces import IRoute, IRouteHandler
    FORGE_ROUTER_AVAILABLE = True
except ImportError:
    ForgeRouter = None
    RouteNotFoundException = Exception
    IRoute = Any
    IRouteHandler = Any
    FORGE_ROUTER_AVAILABLE = False
    # Define a mock RouteService if forge_router is not available
    class RouteService:
        """Mock RouteService for backward compatibility."""
        
        def __init__(self):
            """Initialize a new RouteService."""
            self._routers = []
        
        def register_router(self, router):
            """Register a router with the service."""
            self._routers.append(router)
        
        def match_route(self, path, method):
            """Match a request path and method to a route."""
            for router in self._routers:
                try:
                    return router.match(path, method)
                except Exception:
                    continue
            return None, {}
        
        def create_handler_with_params(self, request):
            """Create a handler function with path parameters."""
            route, params = self.match_route(request.path, request.method)
            if route is None:
                raise ValueError(f"No route found for {request.method} {request.path}")
            
            if isinstance(route, dict):
                handler = route["handler"]
            else:
                handler = route.handler
            
            async def handler_with_params(req):
                return await handler(req, **params)
            
            return handler_with_params

from forge_core.router import SimpleRouter
from forge_core.interfaces import IRequest, IResponse


class RouterBridge:
    """Bridge between SimpleRouter and forge_router.Router.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_router.RouterBridge class instead.
    
    This class adapts the SimpleRouter interface to work with forge_router.Router,
    making it easier to migrate code that uses SimpleRouter to use the new Router.
    """
    
    def __init__(self) -> None:
        """Initialize a new RouterBridge.
        
        If forge_router is available, this will use the new Router implementation.
        Otherwise, it will fall back to SimpleRouter.
        """
        if FORGE_ROUTER_AVAILABLE:
            self._router = ForgeRouter()
        else:
            self._router = SimpleRouter()
    
    @property
    def routes(self) -> List[Any]:
        """Get all routes registered with this router."""
        return self._router.routes
    
    @property
    def middleware(self) -> List[Any]:
        """Get middleware applied to all routes in this router."""
        return getattr(self._router, 'middleware', [])
    
    def add_middleware(self, middleware: Any) -> None:
        """Add middleware to the router.
        
        Args:
            middleware: The middleware to add.
        """
        if hasattr(self._router, 'add_middleware'):
            self._router.add_middleware(middleware)
        elif hasattr(self._router, '_middlewares'):
            self._router._middlewares.append(middleware)
    
    def add_route(self, path: str, handler: Callable, methods: List[str] = None) -> None:
        """Add a route to the router.
        
        Args:
            path: The URL path pattern.
            handler: The handler function.
            methods: The HTTP methods to match. Defaults to ["GET"].
        """
        methods = methods or ["GET"]
        
        if isinstance(self._router, SimpleRouter):
            self._router.add_route(path, handler, methods)
        else:
            # Adapt the handler to match the IRouteHandler interface expected by forge_router
            async def route_handler(request: Any, **kwargs: Any) -> Any:
                return await handler(request, **kwargs)
            
            self._router.add_route(path, route_handler, methods)
    
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
        try:
            return self._router.match(path, method)
        except RouteNotFoundException as e:
            # Convert RouteNotFoundException to ValueError for backward compatibility
            raise ValueError(str(e))


def create_router() -> Union[SimpleRouter, Any]:
    """Create a router instance.
    
    DEPRECATED: This function is deprecated and will be removed in a future version.
    Please use forge_router.create_router instead.
    
    If forge_router is available, this will create a Router instance.
    Otherwise, it will create a SimpleRouter instance.
    
    Returns:
        A router instance.
    """
    if FORGE_ROUTER_AVAILABLE:
        return ForgeRouter()
    else:
        return SimpleRouter() 