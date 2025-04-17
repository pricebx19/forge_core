"""Tests for the Middleware system."""

import pytest

# Use package imports for consistent importing
from forge_core.middleware import Middleware, MiddlewareStack
from forge_core.request import Request
from forge_core.response import Response


class MockTestMiddleware(Middleware):
    """Test middleware that records its execution."""
    
    def __init__(self, name, events):
        self.name = name
        self.events = events
        
    async def process(self, request, next):
        self.events.append(f"{self.name}_before")
        request.attributes[self.name] = True
        response = await next(request)
        self.events.append(f"{self.name}_after")
        response.headers[f"X-{self.name}"] = "Processed"
        return response


class ErrorMiddleware(Middleware):
    """Middleware that raises an exception."""
    
    async def process(self, request, next):
        raise ValueError("Test error")


class HandlingMiddleware(Middleware):
    """Middleware that handles errors from subsequent middleware."""
    
    async def process(self, request, next):
        try:
            return await next(request)
        except ValueError:
            return Response(content="Error caught", status_code=500)


async def test_middleware_stack_execution():
    """Test that middleware stack executes middleware in the correct order."""
    events = []
    
    middleware1 = MockTestMiddleware("first", events)
    middleware2 = MockTestMiddleware("second", events)
    
    stack = MiddlewareStack()
    stack.add(middleware1)
    stack.add(middleware2)
    
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        events.append("handler")
        assert req.attributes.get("first") is True
        assert req.attributes.get("second") is True
        return Response(content="Response", status_code=200)
    
    response = await stack.process(request, handler)
    
    assert events == ["first_before", "second_before", "handler", "second_after", "first_after"]
    assert response.headers["X-first"] == "Processed"
    assert response.headers["X-second"] == "Processed"


async def test_middleware_error_handling():
    """Test that middleware can handle errors from subsequent middleware."""
    stack = MiddlewareStack()
    stack.add(HandlingMiddleware())
    stack.add(ErrorMiddleware())
    
    request = Request(method="GET", url="/test")
    
    async def handler(req):
        # This should never be called
        pytest.fail("Handler should not be called")
    
    response = await stack.process(request, handler)
    
    assert response.status_code == 500
    assert response.content == b"Error caught"


async def test_middleware_removal():
    """Test that middleware can be removed from the stack."""
    middleware1 = MockTestMiddleware("first", [])
    middleware2 = MockTestMiddleware("second", [])
    
    stack = MiddlewareStack()
    stack.add(middleware1)
    stack.add(middleware2)
    
    assert len(stack.stack) == 2
    
    stack.remove(middleware1)
    
    assert len(stack.stack) == 1
    assert stack.stack[0] == middleware2


async def test_middleware_insertion():
    """Test that middleware can be inserted at a specific position."""
    middleware1 = MockTestMiddleware("first", [])
    middleware2 = MockTestMiddleware("second", [])
    middleware3 = MockTestMiddleware("third", [])
    
    stack = MiddlewareStack()
    stack.add(middleware1)
    stack.add(middleware3)
    
    assert len(stack.stack) == 2
    
    stack.insert(1, middleware2)
    
    assert len(stack.stack) == 3
    assert stack.stack[0] == middleware1
    assert stack.stack[1] == middleware2
    assert stack.stack[2] == middleware3 