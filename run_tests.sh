#!/bin/bash
# Script to install forge_core in development mode and run tests

# Install the package in development mode
echo "Installing forge_core in development mode..."
pip install -e .

# Run the tests
echo "Running tests..."
pytest 