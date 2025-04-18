"""Tests for ASGI integration in the Kernel class."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from forge_core.kernel import Kernel
from forge_http import Request
from forge_http import Response


class MockApp:
    def __init__(self):
        self.config = MagicMock()
        self.middleware = MagicMock()
        self.lifecycle = MagicMock()


@pytest.fixture
def kernel():
    """Create a kernel for testing."""
    app = MockApp()
    return Kernel(app)


async def test_create_request(kernel):
    """Test that the kernel can create a request from ASGI scope."""
    scope = {
        "method": "POST",
        "path": "/test",
        "headers": [(b"content-type", b"application/json")],
        "query_string": b"param=value"
    }
    receive = MagicMock()
    
    request = kernel._create_request(scope, receive)
    
    assert request.method == "POST"
    assert request.path == "/test"


async def test_send_response(kernel):
    """Test that responses can be sent correctly."""
    response = Response(content=b"Test", status_code=200)
    send = AsyncMock()  # Use AsyncMock instead of MagicMock
    
    await kernel._send_response(response, send)
    
    send.assert_awaited()  # Use assert_awaited instead of assert_called
    assert len(send.await_args_list) == 2  # Should be called twice - once for headers, once for body


async def test_handle_request_success(kernel):
    """Test that requests can be handled successfully."""
    # Mock the required methods
    mock_request = Request(method="GET", url="/test")
    mock_response = Response(content="Success", status_code=200)
    
    kernel._create_request = AsyncMock(return_value=mock_request)
    kernel._app.middleware.process_request = MagicMock(return_value=mock_request)
    kernel._app.middleware.process_response = MagicMock(return_value=mock_response)
    kernel._send_response = AsyncMock()
    
    # Create a mock route with a handler
    mock_route = {"handler": AsyncMock(return_value=mock_response)}
    kernel._match_route = MagicMock(return_value=(mock_route, {}))
    
    # Call the handler
    scope = {"method": "GET", "path": "/test"}
    receive = AsyncMock()
    send = AsyncMock()
    
    await kernel._handle_request(scope, receive, send)
    
    kernel._send_response.assert_awaited_once_with(mock_response, send)


async def test_handle_request_not_found(kernel):
    """Test that 404 responses are returned when no route is found."""
    # Mock the required methods
    mock_request = Request(method="GET", url="/test")
    mock_response = Response(content="Not Found", status_code=404)
    
    kernel._create_request = AsyncMock(return_value=mock_request)
    kernel._app.middleware.process_request = MagicMock(return_value=mock_request)
    kernel._app.middleware.process_response = MagicMock(return_value=mock_response)
    kernel._create_not_found_response = MagicMock(return_value=mock_response)
    kernel._send_response = AsyncMock()
    
    # Return None for route to simulate no match
    kernel._match_route = MagicMock(return_value=(None, {}))
    
    # Call the handler
    scope = {"method": "GET", "path": "/test"}
    receive = AsyncMock()
    send = AsyncMock()
    
    await kernel._handle_request(scope, receive, send)
    
    # Verify that a 404 response was sent
    kernel._send_response.assert_awaited_once_with(mock_response, send)


async def test_handle_request_exception(kernel):
    """Test that exceptions during request handling are handled correctly."""
    # Mock the required methods
    mock_request = Request(method="GET", url="/test")
    mock_error_response = Response(content="Error", status_code=500)
    
    kernel._create_request = AsyncMock(return_value=mock_request)
    kernel._app.middleware.process_request = MagicMock(return_value=mock_request)
    kernel._app.middleware.process_exception = MagicMock(return_value=mock_error_response)
    kernel._app.middleware.process_response = MagicMock(return_value=mock_error_response)
    kernel._send_response = AsyncMock()
    
    # Create a mock route with a handler that raises an exception
    async def failing_handler(request):
        raise ValueError("Test error")
    
    mock_route = {"handler": failing_handler}
    kernel._match_route = MagicMock(return_value=(mock_route, {}))
    
    # Call the handler
    scope = {"method": "GET", "path": "/test"}
    receive = AsyncMock()
    send = AsyncMock()
    
    await kernel._handle_request(scope, receive, send)
    
    kernel._send_response.assert_awaited_once_with(mock_error_response, send)


async def test_handle_request_uncaught_exception(kernel):
    """Test that uncaught exceptions are handled correctly."""
    # Mock the required methods
    mock_request = Request(method="GET", url="/test")
    
    kernel._create_request = AsyncMock(return_value=mock_request)
    kernel._app.middleware.process_request = MagicMock(side_effect=ValueError("Uncaught error"))
    kernel._send_response = AsyncMock()
    
    # Call the handler
    scope = {"method": "GET", "path": "/test"}
    receive = AsyncMock()
    send = AsyncMock()
    
    await kernel._handle_request(scope, receive, send)
    
    # Verify that an error response was sent
    assert kernel._send_response.await_args[0][0].status == 500


async def test_handle_request_async_handler(kernel):
    """Test that the kernel can handle async route handlers."""
    # Mock the required methods
    mock_request = Request(method="GET", url="/test")
    mock_response = Response(content="Async Success", status_code=200)
    
    kernel._create_request = AsyncMock(return_value=mock_request)
    kernel._app.middleware.process_request = MagicMock(return_value=mock_request)
    kernel._app.middleware.process_response = MagicMock(return_value=mock_response)
    kernel._send_response = AsyncMock()
    
    # Create an async handler using AsyncMock
    async_handler = AsyncMock(return_value=mock_response)
    
    # Create a mock route with the async handler
    mock_route = {"handler": async_handler}
    kernel._match_route = MagicMock(return_value=(mock_route, {}))
    
    # Call the handler
    scope = {"method": "GET", "path": "/test"}
    receive = AsyncMock()
    send = AsyncMock()
    
    await kernel._handle_request(scope, receive, send)
    
    kernel._send_response.assert_awaited_once_with(mock_response, send) 