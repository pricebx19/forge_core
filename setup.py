#!/usr/bin/env python
"""Setup script for the forge_core package."""

from setuptools import setup, find_packages

setup(
    name="forge_core",
    version="0.1.0",
    description="Core HTTP lifecycle, request handling, and response flow for the Forge Framework",
    author="Forge Framework",
    author_email="forge@example.com",
    py_modules=[
        "app",
        "config",
        "kernel",
        "lifecycle",
        "middleware",
        "request",
        "response",
        "__init__",
    ],
    install_requires=[
        "typing-extensions>=4.5.0",
    ],
    python_requires=">=3.8",
) 