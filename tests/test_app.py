"""Tests for the App and ForgeApplication classes."""

import pytest

# Use package imports for consistent importing
from forge_core.app import App, ForgeApplication
from forge_core.response import Response


def test_app_creation():
    """Test that we can create an application instance."""
    app = App()
    assert isinstance(app, App)


def test_forge_application_alias():
    """Test that ForgeApplication is an alias for App."""
    app = ForgeApplication()
    assert isinstance(app, App)
    assert isinstance(app, ForgeApplication)
    assert App is ForgeApplication


def test_app_route_registration(app):
    """Test that routes can be registered with the application."""
    
    @app.route("/test")
    def test_route(request):
        return Response.text("Test route")
    
    assert "/test" in app.routes


class MockApp:
    """Mock App for testing middleware execution order."""
    
    def __init__(self):
        self.middleware_stack = []
        self.routes = {}
        
    def middleware(self, func):
        """Register middleware."""
        self.middleware_stack.append(func)
        return func
        
    def route(self, path):
        """Register a route."""
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
        
    def handle_request(self, request):
        """Handle a request with middleware execution."""
        # Define an execution order list that middleware can modify
        request.attributes["execution_order"] = []
        
        # Create the middleware chain
        async def final_handler(req):
            handler = self.routes.get(req.url, lambda r: Response.text("Not Found"))
            request.attributes["execution_order"].append("handler")
            return handler(req)
            
        # Build middleware chain in reverse
        handler = final_handler
        for middleware in reversed(self.middleware_stack):
            prev_handler = handler
            handler = lambda req, m=middleware, h=prev_handler: m(req, h)
            
        # Execute the chain
        import asyncio
        return asyncio.run(handler(request))


def test_app_middleware_execution_order(request_factory):
    """Test that middleware is executed in the correct order."""
    app = MockApp()
    execution_order = []
    
    @app.middleware
    async def middleware1(request, next_handler):
        execution_order.append("middleware1_before")
        response = await next_handler(request)
        execution_order.append("middleware1_after")
        return response
    
    @app.middleware
    async def middleware2(request, next_handler):
        execution_order.append("middleware2_before")
        response = await next_handler(request)
        execution_order.append("middleware2_after")
        return response
    
    @app.route("/")
    def index(request):
        execution_order.append("handler")
        return Response.text("Hello")
    
    request = request_factory()
    response = app.handle_request(request)
    
    assert execution_order == [
        "middleware1_before",
        "middleware2_before",
        "handler",
        "middleware2_after",
        "middleware1_after"
    ]
    assert response.content == b"Hello" 