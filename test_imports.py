#!/usr/bin/env python
"""Test script to verify imports are working."""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    print("Attempting to import modules...")
    
    # Try importing each module separately
    print("\nImporting config...")
    from forge_core import config
    print("✓ Config module imported successfully")
    
    print("\nImporting request...")
    from forge_core import request
    print("✓ Request module imported successfully")
    
    print("\nImporting response...")
    from forge_core import response
    print("✓ Response module imported successfully")
    
    print("\nImporting middleware...")
    from forge_core import middleware
    print("✓ Middleware module imported successfully")
    
    print("\nImporting lifecycle...")
    from forge_core import lifecycle
    print("✓ Lifecycle module imported successfully")
    
    print("\nImporting kernel...")
    from forge_core import kernel
    print("✓ Kernel module imported successfully")
    
    print("\nImporting app...")
    from forge_core import app
    print("✓ App module imported successfully")
    
    print("\nAll modules imported successfully!")
    print("\nTrying to create basic objects...")
    
    config_obj = config.Config()
    print("✓ Created Config object")
    
    # Try to import and create the App class directly
    try:
        from forge_core.app import App
        app_obj = App()
        print("✓ Created App object")
    except Exception as e:
        print(f"✗ Failed to create App object: {type(e).__name__}: {str(e)}")
    
    print("\nBasic import test complete.")
        
except Exception as e:
    print(f"✗ Import error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc() 