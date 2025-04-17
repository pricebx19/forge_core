#!/usr/bin/env python
"""Test runner that fixes import paths and runs all tests."""

import os
import sys
import subprocess
from pathlib import Path

# Get the absolute path to the current directory
current_dir = Path(__file__).parent.absolute()

def run_tests():
    """Run the tests with the proper import path set up."""
    # Configure environment for the subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir)
    
    print(f"Setting PYTHONPATH to: {current_dir}")
    print("Running simple import test...")
    
    # First run our simple import test
    result = subprocess.run(
        [sys.executable, "test_simple_flat.py"],
        env=env,
        cwd=current_dir
    )
    
    if result.returncode != 0:
        print("Simple test failed. Cannot continue.")
        return result.returncode
    
    print("\nRunning pytest...")
    
    # Then run pytest if the simple test passes
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests"],
        env=env,
        cwd=current_dir
    )
    
    return result.returncode

if __name__ == "__main__":
    # Create a simple test file that doesn't use package imports
    simple_test = """
import sys

# Import modules directly
try:
    import app
    import config
    import request
    import response
    import kernel
    import middleware
    import lifecycle
    
    print("✓ SUCCESS: All core modules imported successfully.")
    
    # Create basic objects to test instantiation
    app_obj = app.App()
    config_obj = config.Config()
    request_obj = request.Request(method="GET", url="/test")
    response_obj = response.Response(content="Test")
    
    print("✓ SUCCESS: All core objects instantiated successfully.")
    
    # Test that the App alias works
    assert app.App is app.ForgeApplication
    print("✓ SUCCESS: App and ForgeApplication are the same class.")
    
    print("\\nSimple import test passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ ERROR: {type(e).__name__}: {str(e)}")
    sys.exit(1)
"""
    
    # Write the simple test to a file
    with open("test_simple_flat.py", "w") as f:
        f.write(simple_test)
    
    # Run the tests
    sys.exit(run_tests()) 