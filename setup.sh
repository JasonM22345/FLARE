#!/bin/bash

# This script sets up the flare environment

# Exit on error
set -e

echo "Starting setup..."

# Install Python 3 and pip
echo "Installing Python 3 and pip..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create a virtual environment in ../FLARE
VENV_DIR="../FLARE"
echo "Creating virtual environment in $VENV_DIR..."
mkdir -p $VENV_DIR
python3 -m venv $VENV_DIR

# Activate the virtual environment
echo "Activating the virtual environment..."
cd $VENV_DIR
source bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing required Python packages..."
REQUIRED_PACKAGES=(
    flask
    requests
    openai
)
for PACKAGE in "${REQUIRED_PACKAGES[@]}"; do
    if pip show $PACKAGE &>/dev/null; then
        echo "$PACKAGE is already installed."
    else
        echo "Installing $PACKAGE..."
        pip install $PACKAGE
    fi
done

echo "Setup completed successfully!"
