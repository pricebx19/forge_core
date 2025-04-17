"""Tests for the Kernel class."""

import pytest
from unittest.mock import MagicMock

# Use package imports for consistent importing
from forge_core.kernel import Kernel
from forge_core.middleware import Middleware, MiddlewareStack
from forge_core.request import Request
from forge_core.response import Response
from forge_core.lifecycle import LifecycleHook, LifecyclePhase, LifecycleManager
from forge_core.config import Config


class MockTestMiddleware(Middleware):
    """Test middleware that adds an attribute to the request."""
    
    def __init__(self, name):
        self.name = name
        self.called = False
        
    async def process(self, request, next):
        self.called = True
        request.attributes[f"middleware_{self.name}"] = True
        return await next(request)


# Create a mock App class for testing
class MockApp:
    def __init__(self):
        self.config = Config()
        self.lifecycle = LifecycleManager(self)
        self.middleware = MiddlewareStack()


async def test_kernel_handle_request():
    """Test that the kernel can handle requests."""
    app = MockApp()
    kernel = Kernel(app)
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        return Response(content="Test Response", status_code=200)
    
    # Mock the handler BEFORE handling the request
    kernel._get_handler = lambda req: handler
    
    response = await kernel.handle(request)
    
    assert response.status_code == 200
    assert response.content == b"Test Response"


async def test_kernel_middleware_stack():
    """Test that middleware is executed in the correct order."""
    app = MockApp()
    kernel = Kernel(app)
    
    middleware1 = MockTestMiddleware("first")
    middleware2 = MockTestMiddleware("second")
    
    app.middleware.add(middleware1)
    app.middleware.add(middleware2)
    
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        assert req.attributes.get("middleware_first") is True
        assert req.attributes.get("middleware_second") is True
        return Response(content="Test Response", status_code=200)
    
    # Mock the handler lookup
    kernel._get_handler = lambda req: handler
    
    response = await kernel.handle(request)
    
    assert middleware1.called is True
    assert middleware2.called is True
    assert response.status_code == 200


async def test_kernel_lifecycle_hooks():
    """Test that lifecycle hooks are executed correctly."""
    app = MockApp()
    kernel = Kernel(app)
    
    events = []
    
    @app.lifecycle.on(LifecyclePhase.BEFORE_REQUEST)
    async def before_request(request):
        events.append("before_request")
        request.attributes["before_request"] = True
        return request
    
    @app.lifecycle.on(LifecyclePhase.AFTER_REQUEST)
    async def after_request(request, response):
        events.append("after_request")
        response.headers["X-Lifecycle"] = "Processed"
        return response
    
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        events.append("handler")
        assert req.attributes.get("before_request") is True
        return Response(content="Test Response", status_code=200)
    
    # Mock the handler lookup
    kernel._get_handler = lambda req: handler
    
    response = await kernel.handle(request)
    
    assert events == ["before_request", "handler", "after_request"]
    assert response.headers["X-Lifecycle"] == "Processed"


async def test_kernel_error_handling():
    """Test that the kernel handles errors correctly."""
    app = MockApp()
    kernel = Kernel(app)
    
    class TestError(Exception):
        pass
    
    @app.lifecycle.on(LifecyclePhase.ERROR)
    async def handle_error(error, request):
        assert isinstance(error, TestError)
        return Response(content="Error handled", status_code=500)
    
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        raise TestError("Test error")
    
    # Mock the handler lookup
    kernel._get_handler = lambda req: handler
    
    response = await kernel.handle(request)
    
    assert response.status_code == 500
    assert response.content == b"Error handled" 