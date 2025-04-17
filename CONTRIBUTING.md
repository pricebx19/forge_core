# Contributing to Forge Core

Thank you for your interest in contributing to Forge Core! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by the Forge Framework Code of Conduct.

## Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/your-username/forge_core.git
cd forge_core
```

2. **Set up a virtual environment with Poetry**

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

3. **Run the tests to verify your setup**

```bash
pytest
```

## Architecture Guidelines

Forge has strict architectural guidelines that all contributions must follow:

1. **One class/function per file**: Each Python file should define exactly one class or function
2. **No logic at module level**: Module-level code should only contain imports, class/function definitions, and simple constant assignments
3. **Use Protocol interfaces**: Interfaces should use `Protocol` from `typing` instead of ABC
4. **Full type annotations**: All functions, methods, and variables must have type annotations
5. **Domain-driven design**: Respect clean architecture boundaries between domain, application, and infrastructure
6. **Composition over inheritance**: Favor composition over inheritance for code reuse
7. **Dependency injection**: Dependencies should be explicitly declared and injected

## Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

   Implement your changes following the architecture guidelines.

3. **Add tests**

   Add tests for your changes. Ensure all tests pass:

```bash
pytest
```

4. **Ensure code quality**

```bash
# Format code with Black
black forge_core tests

# Sort imports with isort
isort forge_core tests

# Run linter (Ruff)
ruff check forge_core tests

# Run type checking
mypy forge_core
```

5. **Commit your changes**

   Use clear, descriptive commit messages:

```bash
git commit -m "Add feature: description of the feature"
```

6. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

7. **Create a pull request**

   Open a pull request against the `main` branch of the Forge repository.

## Pull Request Requirements

For a pull request to be accepted, it must:

- Pass all automated tests
- Maintain or improve code coverage
- Follow all architectural guidelines
- Include appropriate documentation updates
- Be reviewed and approved by at least one maintainer

## Project Structure

Each Forge component follows this standard structure:

```
forge_core/
├── domain/
│   ├── entities/
│   ├── services/
│   └── interfaces/
├── application/
│   └── use_cases/
├── infrastructure/
│   └── adapters/
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── README.md
```

## Documentation

- Update the README.md if your changes affect the public API or usage
- Include docstrings for all public functions, classes, and methods
- Follow Google-style docstrings for consistency

## Release Process

Forge follows semantic versioning:

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

Releases are managed by the maintainers and triggered by tagging the repository.

## Questions?

If you have any questions about contributing, please open an issue or reach out to the maintainers.

Thank you for contributing to Forge Core!
