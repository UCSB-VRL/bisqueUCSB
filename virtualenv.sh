#!/bin/bash
# Updated by Wahid Sadique Koly on 2025-07-29 to align with the new upgraded codebase.

# Use Python 3's built-in venv module instead of virtualenv
# This is the modern approach for Python 3
echo "Setting up Python 3 virtual environment..."

# Create virtual environment using Python 3's venv module
python3 -m venv /usr/lib/bisque

# Activate the virtual environment and upgrade pip
source /usr/lib/bisque/bin/activate
python -m pip install --upgrade pip setuptools wheel

echo "Python 3 virtual environment setup complete"
