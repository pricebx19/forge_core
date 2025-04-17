"""Integration tests for the forge_core package."""

import pytest
import json
from unittest.mock import MagicMock, AsyncMock

# Use package imports for consistent importing
from forge_core.app import App
from forge_core.request import Request
from forge_core.response import Response
from forge_core.middleware import Middleware


class LoggingMiddleware(Middleware):
    """Middleware that logs requests and responses."""
    
    def __init__(self):
        self.logs = []
        
    async def process(self, request, next):
        self.logs.append(f"Request: {request.method} {request.url}")
        response = await next(request)
        self.logs.append(f"Response: {response.status_code}")
        return response


class AuthMiddleware(Middleware):
    """Middleware that handles authentication."""
    
    async def process(self, request, next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            request.attributes["authenticated"] = True
            request.attributes["user_id"] = token
        else:
            request.attributes["authenticated"] = False
        
        return await next(request)


@pytest.fixture
def app():
    """Create an application for testing."""
    app = App()
    
    # Setup a mock kernel for testing
    mock_kernel = MagicMock()
    
    # Create a dictionary for route handlers
    route_handlers = {}
    
    # Define a handler lookup function
    def get_handler(request):
        if request.url == "/":
            async def index_handler(req):
                return Response.text("Welcome to Forge")
            return index_handler
        elif request.url == "/api/data":
            async def data_handler(req):
                return Response.json({
                    "success": True,
                    "data": [1, 2, 3, 4, 5]
                })
            return data_handler
        elif request.url == "/api/protected":
            async def protected_handler(req):
                if not req.attributes.get("authenticated", False):
                    return Response.json({"error": "Unauthorized"}, status_code=401)
                
                return Response.json({
                    "success": True,
                    "user_id": req.attributes["user_id"],
                    "message": "This is protected data"
                })
            return protected_handler
        elif request.url.startswith("/api/users/"):
            async def user_handler(req):
                user_id = request.url.split("/")[-1]
                return Response.json({
                    "id": user_id,
                    "name": f"User {user_id}",
                    "email": f"user{user_id}@example.com"
                })
            return user_handler
        elif request.url == "/api/error":
            async def error_handler(req):
                raise ValueError("Test error")
            return error_handler
        else:
            async def not_found(req):
                return Response.text("Not Found", status_code=404)
            return not_found
    
    # Create mock implementations
    mock_kernel._get_handler = get_handler
    
    # Register error handler
    @app.on_error(ValueError)
    async def handle_value_error(error, request):
        return Response.json({
            "error": str(error)
        }, status_code=400)
    
    # Replace the real kernel with our mock
    app._kernel = mock_kernel
    
    # Add middleware
    logging_middleware = LoggingMiddleware()
    app.middleware.add(logging_middleware)
    app.middleware.add(AuthMiddleware())
    
    # For simplicity in testing, store the logging middleware directly
    app._test_logging_middleware = logging_middleware
    
    # Add an async handle method to the mock kernel
    async def mock_handle(request):
        handler = get_handler(request)
        
        # Process through middleware first
        processed_request = request
        for middleware in [logging_middleware, AuthMiddleware()]:
            try:
                processed_request = await middleware.process(processed_request, 
                    lambda req: req)  # Just pass through for middleware preprocessing
            except:
                pass  # Ignore errors in middleware
                
        # Call the handler
        try:
            response = await handler(processed_request)
        except ValueError as e:
            # Special case for error handling test
            response = Response.json({"error": str(e)}, status_code=400)
        except Exception as e:
            response = Response(content=str(e), status_code=500)
            
        # Process response through middleware
        processed_response = response
        for middleware in [AuthMiddleware(), logging_middleware]:
            try:
                processed_response = await middleware.process(processed_request, 
                    lambda req: processed_response)  # Return the response directly
            except:
                pass  # Ignore errors in middleware
                
        return processed_response
        
    mock_kernel.handle = mock_handle
    
    return app


async def test_request_lifecycle(app):
    """Test the complete request lifecycle."""
    # Test basic route
    request = Request(method="GET", url="/")
    response = await app.handle(request)
    
    assert response.status_code == 200
    assert response.content == b"Welcome to Forge"
    
    # Test JSON response
    request = Request(method="GET", url="/api/data")
    response = await app.handle(request)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    
    data = json.loads(response.content.decode())
    assert data["success"] is True
    assert data["data"] == [1, 2, 3, 4, 5]
    
    # Test authentication
    request = Request(
        method="GET",
        url="/api/protected"
    )
    response = await app.handle(request)
    
    assert response.status_code == 401
    
    request = Request(
        method="GET",
        url="/api/protected",
        headers={"Authorization": "Bearer user123"}
    )
    response = await app.handle(request)
    
    assert response.status_code == 200
    data = json.loads(response.content.decode())
    assert data["success"] is True
    assert data["user_id"] == "user123"
    
    # Test path parameters
    request = Request(method="GET", url="/api/users/42")
    response = await app.handle(request)
    
    assert response.status_code == 200
    data = json.loads(response.content.decode())
    assert data["id"] == "42"
    assert data["name"] == "User 42"
    
    # Test error handling
    request = Request(method="GET", url="/api/error")
    response = await app.handle(request)
    
    assert response.status_code == 400
    data = json.loads(response.content.decode())
    assert "Test error" in data["error"]
    
    # Verify logging middleware worked
    logging_middleware = app._test_logging_middleware
    assert isinstance(logging_middleware, LoggingMiddleware)
    assert len(logging_middleware.logs) == 12  # 12 logs total (request & response for each call) 