#!/usr/bin/env python3
"""
Setup script for Gmail Filtering System
"""

from setuptools import find_packages, setup

setup(
    name="gmail-filtering-system",
    version="0.1.0",
    description="Gmail data extraction and filtering system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pre-commit",
            "black",
            "isort",
            "flake8",
        ],
    },
)
