# Forge Core Architecture

This document outlines the architecture of the Forge Core framework and its components.

## Overview

Forge Core is the central component of the Forge framework, providing the core infrastructure for building web applications.

The architecture follows a modular, service-oriented approach with clear separation of concerns and a focus on extensibility.

## Key Components

### App Class

The `App` class is the main entry point for Forge applications. It:

- Manages the application lifecycle
- Handles dependency injection through the container
- Coordinates services, middleware, and routers
- Provides a consistent API for application components

### Service Layer

The framework is built on a modular service-oriented architecture. Each major piece of functionality is provided by a dedicated service, potentially in its own package:

#### HTTP Service

The `HttpService` in forge_core handles HTTP requests, delegating routing to the RouteService from forge_router.

#### Event Service

The `EventService` in `forge_events` package implements an event-driven architecture, allowing components to publish and subscribe to events. This helps decouple components and makes the system more extensible.

#### Error Service

The `ErrorService` in `forge_errors` package centralizes error handling, providing a consistent way to handle and report errors across the application.

### Router Architecture

The routing logic is in the `forge_router` package, providing a more robust and flexible routing system:

- The `Router` class in forge_router handles URL routing
- The `RouteService` provides a higher-level API for route matching and handler retrieval
- The `RouterBridge` in forge_core facilitates backward compatibility and migration from the old routing system

### Kernel

The `Kernel` class handles HTTP request processing, including:

- Middleware execution
- Lifecycle hooks
- Error handling

The Kernel has been refactored to delegate most of its responsibilities to specialized services, following the single responsibility principle.

## Package Structure

The Forge framework is divided into multiple packages, each with its own responsibility:

- **forge_core**: Core application functionality, lifecycle management, and coordination
- **forge_router**: URL routing and request handling
- **forge_events**: Event-driven architecture implementation
- **forge_errors**: Centralized error handling
- **forge_http**: HTTP request and response handling
- **forge_config**: Configuration management
- **forge_orm**: Object-relational mapping
- And more...

## Architectural Patterns

### Dependency Injection

Forge Core uses dependency injection extensively to promote loose coupling and testability. The `Container` class from the kink library is used for this purpose.

### Event-Driven Architecture

The event system allows components to communicate without direct dependencies, enhancing modularity and extensibility.

### Service Registry

The `ServiceRegistry` provides a centralized registry for services, making it easy to discover and use services throughout the application.

### Middleware Pattern

The middleware pattern allows for request/response processing in a modular, composable way.

## Flow of Requests

1. A request comes into the Kernel
2. The Kernel passes the request to the middleware stack
3. The HttpService uses the RouteService from forge_router to match the request to a route
4. The matched handler is executed
5. The response goes back through the middleware stack
6. The Kernel sends the response to the client

## Error Handling

Errors are handled at different levels:

1. Handler-level error handling
2. Service-level error handling using the ErrorService from forge_errors
3. Global error handling in the Kernel

## Events

Key events in the system include:

- `application.starting`
- `application.stopping`
- `application.stopped`
- `request.received`
- `request.completed`
- `request.error`

## Extensions

The architecture is designed to be extensible through:

- Custom services
- Middleware
- Event subscribers
- Error handlers

## Backward Compatibility

To maintain backward compatibility with older Forge applications, bridge classes have been implemented for router handling and other critical components.
