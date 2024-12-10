#!/bin/bash

# This script sets up the FLARE environment

# Exit on error
set -e

echo "Starting setup..."

# Fix: Ensure script uses Unix-style line endings
if [[ "$(uname -s)" == "Linux" ]]; then
    dos2unix "$0" 2>/dev/null || true
fi

# Install Python 3 and pip
echo "Installing Python 3, pip, and venv..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create a virtual environment in ../FLARE
VENV_DIR="../FLARE"
echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment. Ensure python3-venv is installed."; exit 1; }

# Activate the virtual environment
echo "Activating the virtual environment..."
cd "$VENV_DIR"
source bin/activate || { echo "Failed to activate the virtual environment."; exit 1; }

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing required Python packages..."
REQUIRED_PACKAGES=(
    flask
    requests
    openai
    pyyaml
)
for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
    if pip show "$PACKAGE" &>/dev/null; then
        echo "$PACKAGE is already installed."
    else
        echo "Installing $PACKAGE..."
        pip install "$PACKAGE"
    fi
done

echo "Setup completed successfully!"
echo "To activate the virtual environment in the future, run: source ../FLARE/bin/activate"

source ../FLARE/bin/activate
