"""Test fixtures and configuration for forge_core."""

import os
import sys
import pytest
from pathlib import Path

# Add the repository root directory to the Python path
# This makes 'forge_core' an importable package
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

# Import the modules using package imports
from forge_core.app import App, ForgeApplication
from forge_core.request import Request
from forge_core.response import Response
from forge_core.config import Config


@pytest.fixture
def app():
    """Create a test application instance."""
    return App()


@pytest.fixture
def config():
    """Create a test configuration instance."""
    return Config()


@pytest.fixture
def request_factory():
    """Create a factory function for test requests."""
    def _create_request(
        method="GET",
        url="/",
        headers=None,
        body=None,
        query_params=None,
        path_params=None
    ):
        return Request(
            method=method,
            url=url,
            headers=headers,
            body=body,
            query_params=query_params,
            path_params=path_params
        )
    return _create_request


@pytest.fixture
def response_factory():
    """Create a factory function for test responses."""
    def _create_response(
        content="",
        status_code=200,
        headers=None
    ):
        return Response(
            content=content,
            status_code=status_code,
            headers=headers
        )
    return _create_response


@pytest.fixture
def json_request():
    """Create a test JSON request."""
    return Request(
        method="POST",
        url="/api/data",
        headers={"Content-Type": "application/json"},
        body=b'{"name": "test", "value": 123}'
    )


@pytest.fixture
def form_request():
    """Create a test form request."""
    return Request(
        method="POST",
        url="/api/form",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=b"name=test&value=123"
    ) 