"""Service layer for the Forge framework.

This module provides service classes that implement business logic and
act as a layer between the HTTP handlers and the data models.
"""

from typing import Any, Dict, Generic, List, Optional, Protocol, TypeVar, Union, cast

from kink import Container

T = TypeVar("T")


class IService(Protocol):
    """Base interface for services in the Forge framework."""
    
    @property
    def container(self) -> Container:
        """Get the DI container used by this service."""
        ...


class BaseService:
    """Base class for services in the Forge framework.
    
    Services implement business logic and provide an interface
    between HTTP handlers and data models/repositories.
    """
    
    def __init__(self, container: Optional[Container] = None) -> None:
        """Initialize a new BaseService.
        
        Args:
            container: Optional dependency injection container. If not provided,
                       a new container will be created.
        """
        self._container = container or Container()
    
    @property
    def container(self) -> Container:
        """Get the dependency injection container used by this service."""
        return self._container
        

class ServiceRegistry:
    """Registry for services in the Forge framework.
    
    This class manages the registration and retrieval of services.
    """
    
    def __init__(self, container: Optional[Container] = None) -> None:
        """Initialize a new ServiceRegistry.
        
        Args:
            container: Optional dependency injection container. If not provided,
                       a new container will be created.
        """
        self._container = container or Container()
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """Register a service with the registry.
        
        Args:
            name: The name of the service.
            service: The service instance.
        """
        self._services[name] = service
        
        # Register the service with the container
        if hasattr(service, "__class__"):
            self._container[service.__class__] = service
    
    def get(self, name: str) -> Any:
        """Get a service by name.
        
        Args:
            name: The name of the service.
            
        Returns:
            The service instance.
            
        Raises:
            KeyError: If no service with the given name is registered.
        """
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """Check if a service is registered.
        
        Args:
            name: The name of the service.
            
        Returns:
            True if a service with the given name is registered.
        """
        return name in self._services
    
    @property
    def container(self) -> Container:
        """Get the dependency injection container used by this registry."""
        return self._container 