# Forge Core

Core HTTP lifecycle, request handling, and response flow for the Forge Framework.

## Overview

This package is part of the [Forge Framework](https://github.com/forge-framework), a comprehensive domain-driven Python web framework. Forge Core provides the central request/response lifecycle management and application kernel.

## Features

- Fully typed HTTP request/response handling
- Middleware stack with dependency injection
- Application lifecycle management
- Clean architecture-compliant request flow
- Protocol-based interface design

## Installation

```bash
pip install forge-core
```

## Usage

```python
from forge_core import ForgeApplication
from forge_core.middleware import MiddlewareStack
from forge_core.response import Response
from forge_core.request import Request

app = ForgeApplication(
    middlewares=MiddlewareStack([
        LoggingMiddleware(),
        AuthenticationMiddleware(),
    ])
)

@app.route("/")
def home(request: Request) -> Response:
    return Response.text("Hello, Forge!")

if __name__ == "__main__":
    app.run()
```

## Architecture

This package follows strict architectural principles:

- Domain-Driven Design
- Clean Architecture
- SOLID principles
- Protocol-based interfaces
- Full type annotations

## Structure

```
forge_core/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── interfaces/
├── application/
│   └── use_cases/
└── infrastructure/
    └── adapters/
```

## Development

1. Clone the repository
2. Install dependencies with Poetry: `poetry install`
3. Run tests: `poetry run pytest`

## Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
