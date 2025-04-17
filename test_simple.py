"""Simple test to verify modules can be imported."""

# This file tests basic imports to ensure modules are accessible
# It doesn't depend on the test framework

import os
import sys

# Make sure we can import modules directly
try:
    from app import App, ForgeApplication
    from config import Config
    from request import Request
    from response import Response
    
    print("✓ SUCCESS: All core modules imported successfully.")
    
    # Create basic objects to test instantiation
    app = App()
    config = Config()
    request = Request(method="GET", url="/test")
    response = Response(content="Test")
    
    print("✓ SUCCESS: All core objects instantiated successfully.")
    
    # Test that the App alias works
    assert App is ForgeApplication
    print("✓ SUCCESS: App and ForgeApplication are the same class.")
    
    print("\nAll tests passed! The module structure is correct.")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {str(e)}")
    print(f"Python path: {sys.path}")
    sys.exit(1) 