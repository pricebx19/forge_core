#!/usr/bin/env python
"""Run tests with the correct Python path setup."""

import os
import sys
import subprocess
from pathlib import Path

# Add the current directory to Python's path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Run pytest
print("Running tests...")
os.environ["PYTHONPATH"] = str(current_dir)
subprocess.run(["pytest", "tests"], check=False) 