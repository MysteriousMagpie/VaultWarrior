#!/bin/bash

# This script sets up the development environment for the AI Vault Planning CLI project.

# Update package list and install necessary packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the project in editable mode with development dependencies
pip install -e .[dev]

echo "Development environment setup complete. Activate the virtual environment with 'source venv/bin/activate'."