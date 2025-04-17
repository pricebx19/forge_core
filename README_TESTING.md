# Testing forge_core

This document explains how to run tests for the forge_core package.

## Setup and Dependencies

Before running tests, you need to install the required dependencies:

```bash
pip install hypercorn httptools orjson multidict pyyaml kink typing-extensions pytest pytest-asyncio pytest-cov
```

## Running Tests

The forge_core package has circular imports that make standard testing challenging. Follow these approaches to run the tests:

### Option 1: Use the run_tests.py script (Recommended)

```bash
python run_tests.py
```

This script will:

1. Install required dependencies
2. Set the correct Python path
3. Run all tests using pytest

### Option 2: Run individual test files

To diagnose issues with specific test files:

```bash
python run_single_tests.py
```

This will run each test file separately and report which ones pass or fail.

### Option 3: Manual testing

If you need to run tests manually:

```bash
# Set PYTHONPATH to include the repo root
# (Replace /path/to/repo with your actual repo path)

# On Windows
set PYTHONPATH=D:\dev\repos\Forge

# On Unix/Linux/Mac
export PYTHONPATH=/path/to/Forge

# Run pytest
pytest forge_core/tests
```

## Common Issues

### ImportError: No module named 'forge_core'

This happens when the 'forge_core' package is not in the Python path. Use one of the scripts above which set the path correctly.

### ImportError: cannot import name 'App' from partially initialized module 'forge_core.app'

This is due to circular imports in the package. The `run_tests.py` script attempts to work around this issue.

## Test Structure

The tests are organized by component:

- `test_config.py`: Tests for the configuration system
- `test_request_response.py`: Tests for HTTP request/response handling
- `test_middleware.py`: Tests for the middleware system
- `test_kernel.py`: Tests for the HTTP kernel
- `test_app.py`: Tests for the main App class
- `test_integration.py`: Integration tests for the complete request lifecycle

## Debugging Individual Tests

To run a specific test function:

```bash
# First set PYTHONPATH as shown above
pytest forge_core/tests/test_config.py::test_config_defaults -v
```
