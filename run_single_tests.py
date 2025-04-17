#!/usr/bin/env python
"""Run individual tests for each component to diagnose issues."""

import os
import sys
import subprocess
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent.absolute()
    
# Get the parent directory (repo root)
repo_dir = script_dir.parent

def setup_environment():
    """Set up the environment for testing."""
    # Configure Python path
    env = os.environ.copy()
    
    # Add the repo root to Python path so "import forge_core" works
    python_path = [str(repo_dir)]
    if "PYTHONPATH" in env:
        python_path.append(env["PYTHONPATH"])
    
    env["PYTHONPATH"] = os.pathsep.join(python_path)
    
    return env

def run_test(test_file):
    """Run a specific test file."""
    env = setup_environment()
    
    print(f"\n----------------------------------------------------")
    print(f"Running test: {test_file}")
    print(f"----------------------------------------------------")
    
    # Run pytest with the specific file
    cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}", "-v"]
    
    result = subprocess.run(
        cmd,
        env=env,
        cwd=script_dir
    )
    
    return result.returncode == 0

def run_single_test_function(test_file, test_function):
    """Run a specific test function."""
    env = setup_environment()
    
    print(f"\n----------------------------------------------------")
    print(f"Running test: {test_file}::{test_function}")
    print(f"----------------------------------------------------")
    
    # Run pytest with the specific test function
    cmd = [sys.executable, "-m", "pytest", f"tests/{test_file}::{test_function}", "-v"]
    
    result = subprocess.run(
        cmd,
        env=env,
        cwd=script_dir
    )
    
    return result.returncode == 0

if __name__ == "__main__":
    # Run each test file separately
    test_files = [
        "test_config.py", 
        "test_request_response.py",
        "test_middleware.py", 
        "test_kernel.py", 
        "test_app.py", 
        "test_integration.py"
    ]
    
    # Start with one simple test to check if basic testing works
    if run_single_test_function("test_config.py", "test_config_defaults"):
        print("\n✓ Basic test functionality is working!")
        
        # Run each test file if the basic test works
        results = {}
        for test_file in test_files:
            results[test_file] = run_test(test_file)
        
        # Print summary
        print("\n----------------------------------------------------")
        print("SUMMARY")
        print("----------------------------------------------------")
        for test_file, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"{status}: {test_file}")
    else:
        print("\n✗ Basic test functionality is not working. Fix this first before running all tests.") 