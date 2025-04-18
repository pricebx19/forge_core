"""Application lifecycle management for the Forge framework.

This module provides the LifecycleManager class for managing the lifecycle of
a Forge application, including startup, shutdown, and request handling events.
"""

import enum
from typing import Any, Callable, Dict, List, Optional, Union, Protocol, TypeVar

T = TypeVar("T")


class LifecyclePhase(enum.Enum):
    """Enumeration of lifecycle phases.
    
    This enum represents the different phases in the application lifecycle
    where hooks can be registered.
    """
    
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    BEFORE_REQUEST = "before_request"
    AFTER_REQUEST = "after_request"
    ERROR = "error"


class LifecycleListener(Protocol):
    """Protocol for lifecycle event listeners."""
    
    def on_event(self, phase: LifecyclePhase, **kwargs: Any) -> Optional[Any]:
        """Handle a lifecycle event.
        
        Args:
            phase: The lifecycle phase that triggered the event.
            **kwargs: Additional data related to the event.
            
        Returns:
            An optional response or modified object.
        """
        ...


class LifecycleHook:
    """A hook registered for a specific lifecycle phase.
    
    This class represents a function to be executed during a specific phase
    of the application lifecycle.
    """
    
    def __init__(self, phase: LifecyclePhase, func: Callable[..., Any]) -> None:
        """Initialize a new LifecycleHook.
        
        Args:
            phase: The lifecycle phase when this hook should be executed.
            func: The function to execute.
        """
        self.phase = phase
        self.func = func
    
    async def execute(self, **kwargs: Any) -> Optional[Any]:
        """Execute the hook function.
        
        Args:
            **kwargs: Arguments to pass to the hook function.
            
        Returns:
            The result of the hook function.
        """
        return await self.func(**kwargs)


class LifecycleManager:
    """Manager for application lifecycle events.
    
    This class manages the lifecycle of a Forge application, including startup,
    shutdown, and request handling events. It allows registering hooks to be
    executed at various points in the application's lifecycle.
    """
    
    def __init__(self, app: Any) -> None:
        """Initialize a new LifecycleManager.
        
        Args:
            app: The Forge application instance.
        """
        self._app = app
        self._hooks: Dict[LifecyclePhase, List[Callable]] = {
            LifecyclePhase.STARTUP: [],
            LifecyclePhase.SHUTDOWN: [],
            LifecyclePhase.BEFORE_REQUEST: [],
            LifecyclePhase.AFTER_REQUEST: [],
            LifecyclePhase.ERROR: [],
        }
        self._started = False
    
    def start(self) -> None:
        """Start the application lifecycle.
        
        This method executes all registered startup hooks and marks the
        application as started.
        """
        if self._started:
            return
        
        # Execute startup hooks
        for hook in self._hooks[LifecyclePhase.STARTUP]:
            hook()
        
        self._started = True
    
    def stop(self) -> None:
        """Stop the application lifecycle.
        
        This method executes all registered shutdown hooks and marks the
        application as stopped.
        """
        if not self._started:
            return
        
        # Execute shutdown hooks in reverse order
        for hook in reversed(self._hooks[LifecyclePhase.SHUTDOWN]):
            hook()
        
        self._started = False
    
    def on(self, phase: LifecyclePhase) -> Callable[[Callable], Callable]:
        """Register a hook to be executed during a specific lifecycle phase.
        
        This is a decorator factory that returns a decorator for registering
        hook functions.
        
        Args:
            phase: The lifecycle phase when the hook should be executed.
            
        Returns:
            A decorator for registering hook functions.
        """
        def decorator(func: Callable) -> Callable:
            self._hooks[phase].append(func)
            return func
        return decorator
    
    def on_startup(self, hook: Callable[[], None]) -> None:
        """Register a hook to be executed on application startup.
        
        Args:
            hook: The hook function to register.
        """
        self._hooks[LifecyclePhase.STARTUP].append(hook)
    
    def on_shutdown(self, hook: Callable[[], None]) -> None:
        """Register a hook to be executed on application shutdown.
        
        Args:
            hook: The hook function to register.
        """
        self._hooks[LifecyclePhase.SHUTDOWN].append(hook)
    
    def on_request_begin(self, hook: Callable[[Any], None]) -> None:
        """Register a hook to be executed when a request begins processing.
        
        Args:
            hook: The hook function to register. It takes a request object as an argument.
        """
        self._hooks[LifecyclePhase.BEFORE_REQUEST].append(hook)
    
    def on_request_end(self, hook: Callable[[Any, Any], None]) -> None:
        """Register a hook to be executed when a request ends processing.
        
        Args:
            hook: The hook function to register. It takes a request and response object
                 as arguments.
        """
        self._hooks[LifecyclePhase.AFTER_REQUEST].append(hook)
    
    def on_error(self, hook: Callable[[Exception, Any], Any]) -> None:
        """Register a hook to be executed when an error occurs during request processing.
        
        Args:
            hook: The hook function to register. It takes an exception and request object
                 as arguments and should return a response.
        """
        self._hooks[LifecyclePhase.ERROR].append(hook)
    
    async def before_request(self, request: Any) -> Any:
        """Execute hooks before a request is processed.
        
        Args:
            request: The request object.
            
        Returns:
            The potentially modified request.
        """
        processed_request = request
        for hook in self._hooks[LifecyclePhase.BEFORE_REQUEST]:
            result = hook(processed_request)
            # Handle both synchronous and asynchronous hooks
            if hasattr(result, "__await__"):
                processed_request = await result
            else:
                processed_request = result
            
            # If a hook returns None, use the original request
            if processed_request is None:
                processed_request = request
        
        return processed_request
    
    async def after_request(self, request: Any, response: Any) -> Any:
        """Execute hooks after a request is processed.
        
        Args:
            request: The request object.
            response: The response object.
            
        Returns:
            The potentially modified response.
        """
        processed_response = response
        for hook in self._hooks[LifecyclePhase.AFTER_REQUEST]:
            result = hook(request, processed_response)
            # Handle both synchronous and asynchronous hooks
            if hasattr(result, "__await__"):
                processed_response = await result
            else:
                processed_response = result
                
            # If a hook returns None, use the original response
            if processed_response is None:
                processed_response = response
        
        return processed_response
    
    async def handle_error(self, error: Exception, request: Any) -> Optional[Any]:
        """Execute hooks when an error occurs during request processing.
        
        Args:
            error: The exception that was raised.
            request: The request object.
            
        Returns:
            The response from the first hook that successfully handles the error,
            or None if no hook successfully handles the error.
        """
        for hook in self._hooks[LifecyclePhase.ERROR]:
            try:
                result = hook(error, request)
                # Handle both synchronous and asynchronous hooks
                if hasattr(result, "__await__"):
                    response = await result
                else:
                    response = result
                
                if response is not None:
                    return response
            except Exception as hook_error:
                # Log the error but continue to the next hook
                print(f"Error in error hook: {hook_error}")
                continue
        
        return None
    
    async def trigger(self, phase: LifecyclePhase, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Trigger hooks for a specific lifecycle phase.
        
        This is a unified entry point for triggering lifecycle hooks,
        which delegates to the appropriate method based on the phase.
        
        Args:
            phase: The lifecycle phase to trigger.
            *args: Positional arguments to pass to the hooks.
            **kwargs: Keyword arguments to pass to the hooks.
            
        Returns:
            The result of the hooks, if any.
        """
        if phase == LifecyclePhase.BEFORE_REQUEST:
            return await self.before_request(args[0] if args else kwargs.get('request'))
        elif phase == LifecyclePhase.AFTER_REQUEST:
            return await self.after_request(
                args[0] if len(args) > 0 else kwargs.get('request'),
                args[1] if len(args) > 1 else kwargs.get('response')
            )
        elif phase == LifecyclePhase.ERROR:
            return await self.handle_error(
                args[0] if len(args) > 0 else kwargs.get('error'),
                args[1] if len(args) > 1 else kwargs.get('request')
            )
        
        return None 