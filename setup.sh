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


# Install go
# Variables
GO_VERSION="1.23.2"
GO_TAR="go${GO_VERSION}.linux-amd64.tar.gz"
GO_URL="https://go.dev/dl/${GO_TAR}"
GO_INSTALL_DIR="/usr/local/go-${GO_VERSION}"

# Download Go tarball
echo "Downloading Go ${GO_VERSION}..."
wget -q --show-progress ${GO_URL} -O ${GO_TAR}

# Extract tarball
echo "Extracting Go tarball..."
tar -xvf ${GO_TAR}

# Move to /usr/local
if [ -d "${GO_INSTALL_DIR}" ]; then
    echo "Removing existing Go installation at ${GO_INSTALL_DIR}..."
    sudo rm -rf ${GO_INSTALL_DIR}
fi

echo "Installing Go to ${GO_INSTALL_DIR}..."
sudo mv go ${GO_INSTALL_DIR}

# Update .bashrc
echo "Updating .bashrc with Go environment variables..."
GO_ENV="\n# Go environment variables\nexport GOROOT=${GO_INSTALL_DIR}\nexport GOPATH=\$HOME/go\nexport PATH=\$GOPATH/bin:\$GOROOT/bin:\$PATH"

if grep -q "export GOROOT=${GO_INSTALL_DIR}" ~/.bashrc; then
    echo "Go environment variables already set in .bashrc. Skipping..."
else
    echo -e "${GO_ENV}" >> ~/.bashrc
    echo "Environment variables added to .bashrc."
fi


# Install crashwalk
#!/bin/bash

# Variables
REPO_URL="https://github.com/bnagy/crashwalk.git"
CLONE_DIR="$HOME/crashwalk"

# Install prerequisites
echo "Installing prerequisites..."
sudo apt update
sudo apt install -y git make gcc

# Clone the Crashwalk repository
echo "Cloning Crashwalk repository..."
if [ -d "${CLONE_DIR}" ]; then
    echo "Directory ${CLONE_DIR} already exists. Removing it to start fresh..."
    rm -rf ${CLONE_DIR}
fi
git clone ${REPO_URL} ${CLONE_DIR}

# Change to the repository directory
cd ${CLONE_DIR}

# Build Crashwalk
echo "Building Crashwalk..."
make

# Verify build
if [ -f "bin/crashwalk" ]; then
    echo "Crashwalk built successfully! The executable is located at ${CLONE_DIR}/bin/crashwalk"
else
    echo "Crashwalk build failed. Check the output above for errors."
    exit 1
fi



\

# Reload .bashrc
echo "Reloading .bashrc..."
source ~/.bashrc

# Verify installation
echo "Verifying Go installation..."
go version

# Cleanup
echo "Cleaning up..."
rm -f ${GO_TAR}

echo "Setup completed successfully!"
echo "To activate the virtual environment in the future, run: source ../FLARE/bin/activate"

source ../FLARE/bin/activate
