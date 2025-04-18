"""Event service for the Forge framework.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the forge_events.EventService class instead.

This module provides services for handling events in an event-driven
architecture. It allows for publishing and subscribing to events.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Union, cast

from forge_core.services import BaseService


class EventSubscriber:
    """Class representing an event subscriber.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_events.EventSubscriber class instead.
    
    An event subscriber is a callable that is invoked when an event is published.
    """
    
    def __init__(
        self, 
        callback: Callable,
        event_name: str,
        priority: int = 0
    ) -> None:
        """Initialize a new EventSubscriber.
        
        Args:
            callback: The function to call when the event is published.
            event_name: The name of the event.
            priority: The priority of the subscriber. Higher priority subscribers
                      are invoked first.
        """
        self.callback = callback
        self.event_name = event_name
        self.priority = priority
    
    async def __call__(self, event_data: Any) -> None:
        """Invoke the subscriber.
        
        Args:
            event_data: The data associated with the event.
        """
        return await self.callback(event_data)


class EventService(BaseService):
    """Service for handling events in an event-driven architecture.
    
    DEPRECATED: This class is deprecated and will be removed in a future version.
    Please use the forge_events.EventService class instead.
    
    This service allows for publishing and subscribing to events, which helps
    decouple components in the application.
    """
    
    def __init__(self, container=None) -> None:
        """Initialize a new EventService.
        
        Args:
            container: Optional dependency injection container.
        """
        super().__init__(container)
        self._subscribers: Dict[str, List[EventSubscriber]] = {}
    
    def subscribe(
        self, 
        event_name: str, 
        callback: Callable,
        priority: int = 0
    ) -> EventSubscriber:
        """Subscribe to an event.
        
        Args:
            event_name: The name of the event.
            callback: The function to call when the event is published.
            priority: The priority of the subscriber. Higher priority subscribers
                      are invoked first.
            
        Returns:
            The event subscriber that was created.
        """
        subscriber = EventSubscriber(callback, event_name, priority)
        
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        
        self._subscribers[event_name].append(subscriber)
        
        # Sort subscribers by priority (highest first)
        self._subscribers[event_name].sort(key=lambda s: -s.priority)
        
        return subscriber
    
    def unsubscribe(self, subscriber: EventSubscriber) -> bool:
        """Unsubscribe from an event.
        
        Args:
            subscriber: The event subscriber to unsubscribe.
            
        Returns:
            True if the subscriber was removed, False otherwise.
        """
        event_name = subscriber.event_name
        
        if event_name not in self._subscribers:
            return False
        
        if subscriber not in self._subscribers[event_name]:
            return False
        
        self._subscribers[event_name].remove(subscriber)
        return True
    
    async def publish(self, event_name: str, event_data: Any = None) -> None:
        """Publish an event.
        
        This invokes all subscribers to the event in priority order.
        
        Args:
            event_name: The name of the event.
            event_data: Optional data associated with the event.
        """
        if event_name not in self._subscribers:
            return
        
        for subscriber in self._subscribers[event_name]:
            await subscriber(event_data)
    
    def get_subscribers(self, event_name: str) -> List[EventSubscriber]:
        """Get all subscribers for an event.
        
        Args:
            event_name: The name of the event.
            
        Returns:
            A list of subscribers for the event.
        """
        return self._subscribers.get(event_name, [])
    
    def has_subscribers(self, event_name: str) -> bool:
        """Check if an event has subscribers.
        
        Args:
            event_name: The name of the event.
            
        Returns:
            True if the event has subscribers, False otherwise.
        """
        return event_name in self._subscribers and len(self._subscribers[event_name]) > 0
    
    def clear(self) -> None:
        """Clear all event subscribers."""
        self._subscribers.clear() 