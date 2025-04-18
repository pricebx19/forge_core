"""Tests for the Request and Response classes."""

import json
import pytest

# Use package imports for consistent importing
from forge_http import Request
from forge_http import Response


def test_request_initialization():
    """Test that the Request can be initialized correctly."""
    request = Request(
        method="GET",
        url="/test",
        headers={"Content-Type": "application/json"},
        query_params={"q": "search"},
        path_params={"id": "123"},
        body=b'{"key": "value"}'
    )
    
    assert request.method == "GET"
    assert request.url == "/test"
    assert request.headers["Content-Type"] == "application/json"
    assert request.query_params["q"] == "search"
    assert request.path_params["id"] == "123"
    assert request.body == b'{"key": "value"}'


def test_request_attributes():
    """Test that request attributes can be set and retrieved."""
    request = Request(method="GET", url="/test")
    
    assert len(request.attributes) == 0
    
    request.attributes["user_id"] = 123
    request.attributes["authenticated"] = True
    
    assert request.attributes["user_id"] == 123
    assert request.attributes["authenticated"] is True
    assert len(request.attributes) == 2


def test_request_content_type():
    """Test that the content type is correctly determined."""
    request = Request(
        method="POST",
        url="/api",
        headers={"Content-Type": "application/json"}
    )
    
    assert request.content_type == "application/json"
    
    request = Request(
        method="POST",
        url="/api",
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    # Content type should be parsed to just the MIME type
    assert request.content_type == "application/json"


def test_request_parsed_body():
    """Test that request body can be parsed correctly."""
    # Test JSON parsing
    request = Request(
        method="POST",
        url="/api",
        headers={"Content-Type": "application/json"},
        body=b'{"name": "test", "value": 123}'
    )
    
    body = request.parsed_body()
    assert body["name"] == "test"
    assert body["value"] == 123
    
    # Test form parsing
    request = Request(
        method="POST",
        url="/form",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=b"name=test&value=123"
    )
    
    body = request.parsed_body()
    assert body["name"] == "test"
    assert body["value"] == "123"


def test_response_initialization():
    """Test that the Response can be initialized correctly."""
    response = Response(
        content=b'{"result": "success"}',
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
    
    assert response.content == b'{"result": "success"}'
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_response_factory_methods():
    """Test the factory methods for creating responses."""
    # Test text response
    response = Response.text("Hello, world!")
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/plain; charset=utf-8"
    assert response.content == b"Hello, world!"
    
    # Test JSON response
    response = Response.json({"name": "test", "value": 123})
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    parsed_content = json.loads(response.content.decode())
    assert parsed_content["name"] == "test"
    assert parsed_content["value"] == 123
    
    # Test HTML response
    response = Response.html("<h1>Hello</h1>")
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.content == b"<h1>Hello</h1>"


def test_response_redirect():
    """Test creating redirect responses."""
    # Test temporary redirect
    response = Response.redirect("/new-location")
    
    assert response.status_code == 302
    assert response.headers["Location"] == "/new-location"
    
    # Test permanent redirect
    response = Response.redirect("/permanent", permanent=True)
    
    assert response.status_code == 301
    assert response.headers["Location"] == "/permanent"


def test_response_error():
    """Test creating error responses."""
    # Test not found
    response = Response.not_found()
    
    assert response.status_code == 404
    
    # Test bad request
    response = Response.bad_request("Invalid input")
    
    assert response.status_code == 400
    assert b"Invalid input" in response.content
    
    # Test server error
    response = Response.server_error("Internal error")
    
    assert response.status_code == 500
    assert b"Internal error" in response.content 