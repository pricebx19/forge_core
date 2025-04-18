"""Tests for the LifecycleManager class."""

import pytest
from unittest.mock import MagicMock

from forge_core.lifecycle import LifecycleManager, LifecyclePhase, LifecycleListener, LifecycleHook
from forge_http import Request
from forge_http import Response


class MockApp:
    def __init__(self):
        pass


@pytest.fixture
def lifecycle_manager():
    app = MockApp()
    return LifecycleManager(app)


async def test_lifecycle_before_request(lifecycle_manager):
    """Test that before request hooks are executed correctly."""
    request = Request(method="GET", url="/test")
    
    # Register a synchronous hook
    def sync_hook(req):
        req.attributes["sync_hook"] = True
        return req
    
    lifecycle_manager.on_request_begin(sync_hook)
    
    # Register an asynchronous hook
    async def async_hook(req):
        req.attributes["async_hook"] = True
        return req
    
    lifecycle_manager.on_request_begin(async_hook)
    
    processed_request = await lifecycle_manager.before_request(request)
    
    assert processed_request.attributes.get("sync_hook") is True
    assert processed_request.attributes.get("async_hook") is True


async def test_lifecycle_after_request(lifecycle_manager):
    """Test that after request hooks are executed correctly."""
    request = Request(method="GET", url="/test")
    response = Response(content="Test", status_code=200)
    
    # Register a synchronous hook
    def sync_hook(req, resp):
        resp.headers["X-Sync-Hook"] = "Executed"
        return resp
    
    lifecycle_manager.on_request_end(sync_hook)
    
    # Register an asynchronous hook
    async def async_hook(req, resp):
        resp.headers["X-Async-Hook"] = "Executed"
        return resp
    
    lifecycle_manager.on_request_end(async_hook)
    
    processed_response = await lifecycle_manager.after_request(request, response)
    
    assert processed_response.headers.get("X-Sync-Hook") == "Executed"
    assert processed_response.headers.get("X-Async-Hook") == "Executed"


async def test_lifecycle_handle_error(lifecycle_manager):
    """Test that error hooks are executed correctly."""
    request = Request(method="GET", url="/test")
    error = ValueError("Test error")
    
    # Register a hook that doesn't handle the error
    def non_handling_hook(err, req):
        # This hook examines the error but doesn't handle it
        assert isinstance(err, ValueError)
        return None
    
    lifecycle_manager.on_error(non_handling_hook)
    
    # Register a hook that handles the error
    def handling_hook(err, req):
        return Response(content="Error handled", status_code=400)
    
    lifecycle_manager.on_error(handling_hook)
    
    response = await lifecycle_manager.handle_error(error, request)
    
    assert response is not None
    assert response.status_code == 400
    assert response.content == b"Error handled"


async def test_lifecycle_handle_error_async(lifecycle_manager):
    """Test that async error hooks are executed correctly."""
    request = Request(method="GET", url="/test")
    error = ValueError("Test error")
    
    # Register an async hook that handles the error
    async def async_handling_hook(err, req):
        return Response(content="Async error handled", status_code=400)
    
    lifecycle_manager.on_error(async_handling_hook)
    
    response = await lifecycle_manager.handle_error(error, request)
    
    assert response is not None
    assert response.status_code == 400
    assert response.content == b"Async error handled"


async def test_lifecycle_handle_error_with_failing_hook(lifecycle_manager):
    """Test that if an error hook fails, we continue to the next one."""
    request = Request(method="GET", url="/test")
    error = ValueError("Test error")
    
    # Register a hook that fails
    def failing_hook(err, req):
        raise RuntimeError("Hook failed")
    
    lifecycle_manager.on_error(failing_hook)
    
    # Register a hook that succeeds
    def succeeding_hook(err, req):
        return Response(content="Second hook handled the error", status_code=500)
    
    lifecycle_manager.on_error(succeeding_hook)
    
    response = await lifecycle_manager.handle_error(error, request)
    
    assert response is not None
    assert response.status_code == 500
    assert response.content == b"Second hook handled the error"


async def test_lifecycle_handle_error_no_handlers(lifecycle_manager):
    """Test that if no error hooks handle the error, None is returned."""
    request = Request(method="GET", url="/test")
    error = ValueError("Test error")
    
    # Don't register any hooks
    
    response = await lifecycle_manager.handle_error(error, request)
    
    assert response is None


def test_lifecycle_start_stop(lifecycle_manager):
    """Test starting and stopping the lifecycle."""
    startup_called = False
    shutdown_called = False
    
    def on_startup():
        nonlocal startup_called
        startup_called = True
    
    def on_shutdown():
        nonlocal shutdown_called
        shutdown_called = True
    
    lifecycle_manager.on_startup(on_startup)
    lifecycle_manager.on_shutdown(on_shutdown)
    
    # Starting the lifecycle should call startup hooks
    lifecycle_manager.start()
    assert startup_called is True
    
    # Starting again shouldn't call hooks again
    startup_called = False
    lifecycle_manager.start()
    assert startup_called is False
    
    # Stopping the lifecycle should call shutdown hooks
    lifecycle_manager.stop()
    assert shutdown_called is True
    
    # Stopping again shouldn't call hooks again
    shutdown_called = False
    lifecycle_manager.stop()
    assert shutdown_called is False


def test_lifecycle_on_decorator(lifecycle_manager):
    """Test the @on decorator for registering hooks."""
    hook_called = False
    
    @lifecycle_manager.on(LifecyclePhase.STARTUP)
    def startup_hook():
        nonlocal hook_called
        hook_called = True
    
    lifecycle_manager.start()
    assert hook_called is True


async def test_lifecycle_hook_execute():
    """Test the LifecycleHook.execute method."""
    called_with = None
    
    async def hook_func(param1, param2):
        nonlocal called_with
        called_with = (param1, param2)
        return "result"
    
    hook = LifecycleHook(LifecyclePhase.BEFORE_REQUEST, hook_func)
    result = await hook.execute(param1="value1", param2="value2")
    
    assert called_with == ("value1", "value2")
    assert result == "result"


async def test_lifecycle_listener():
    """Test that a LifecycleListener can handle events."""
    class TestListener(LifecycleListener):
        def on_event(self, phase, **kwargs):
            if phase == LifecyclePhase.STARTUP:
                kwargs['app'].startup_called = True
            elif phase == LifecyclePhase.SHUTDOWN:
                kwargs['app'].shutdown_called = True
            elif phase == LifecyclePhase.BEFORE_REQUEST:
                # Modify the request
                kwargs["request"].attributes["listener_modified"] = True
                return kwargs["request"]
            elif phase == LifecyclePhase.ERROR:
                # Handle the error
                return Response(content="Listener handled error", status_code=418)
            return None
    
    listener = TestListener()
    app = MockApp()
    
    # Test BEFORE_REQUEST phase
    request = Request(method="GET", url="/test")
    result = listener.on_event(LifecyclePhase.BEFORE_REQUEST, request=request)
    
    assert result is request
    assert request.attributes.get("listener_modified") is True
    
    # Test ERROR phase
    error = ValueError("Test error")
    response = listener.on_event(LifecyclePhase.ERROR, error=error, request=request)
    
    assert response is not None
    assert response.status_code == 418
    assert response.content == b"Listener handled error" 