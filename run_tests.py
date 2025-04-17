#!/usr/bin/env python
"""Run tests with a properly configured import path.

This script adds the parent directory to Python's import path,
allowing the forge_core module to be imported correctly.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies for testing."""
    print("Installing required dependencies...")
    
    # Basic dependencies from pyproject.toml
    deps = [
        "hypercorn",
        "httptools",
        "orjson", 
        "multidict",
        "pyyaml",
        "kink",
        "typing-extensions",
        # Testing dependencies
        "pytest",
        "pytest-asyncio",
        "pytest-cov"
    ]
    
    cmd = [sys.executable, "-m", "pip", "install"] + deps
    print(f"Running: {' '.join(cmd)}")
    
    subprocess.run(cmd, check=True)
    print("Dependencies installed successfully.")

def run_tests():
    """Run tests with proper path setup."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Get the parent directory (repo root)
    repo_dir = script_dir.parent
    
    # Install dependencies before running tests
    install_dependencies()
    
    # Configure Python path for the subprocess
    env = os.environ.copy()
    
    # Add the repo root to Python path so "import forge_core" works
    python_path = [str(repo_dir)]
    if "PYTHONPATH" in env:
        python_path.append(env["PYTHONPATH"])
    
    env["PYTHONPATH"] = os.pathsep.join(python_path)
    
    # Print information
    print(f"\nRunning tests with PYTHONPATH: {env['PYTHONPATH']}")
    
    # Run pytest in the forge_core directory
    cmd = [sys.executable, "-m", "pytest", "tests"]
    
    print(f"Running command: {' '.join(cmd)}")
    
    return subprocess.run(
        cmd,
        env=env,
        cwd=script_dir
    ).returncode

if __name__ == "__main__":
    sys.exit(run_tests()) 