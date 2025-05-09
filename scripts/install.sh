#!/bin/bash
# Main installation script for Bird Camera system

set -e  # Exit on error

# Get directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Display welcome message
echo "=========================================="
echo "Bird Camera System Installation"
echo "=========================================="
echo

# Step 1: Install dependencies
echo "Step 1: Installing system dependencies..."
if [ -f "$SCRIPT_DIR/setup/setup.sh" ]; then
    bash "$SCRIPT_DIR/setup/setup.sh"
else
    echo "Warning: setup.sh not found, skipping dependency installation."
    echo "You may need to install dependencies manually."
fi

# Step 2: Install Python requirements
echo
echo "Step 2: Installing Python requirements..."
pip3 install -r "$PROJECT_ROOT/requirements.txt"

# Step 3: Configure environment
echo
echo "Step 3: Setting up environment configuration..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    cp "$PROJECT_ROOT/config/env.example" "$PROJECT_ROOT/.env"
    echo "Created .env file from example template."
    echo "Please edit this file to match your configuration:"
    echo "nano $PROJECT_ROOT/.env"
else
    echo ".env file already exists, skipping creation."
fi

# Step 4: Configure service
echo
echo "Step 4: Configuring service file..."
if [ -f "$SCRIPT_DIR/service/bird_cam.service" ]; then
    # Get current user and home directory
    CURRENT_USER=$(whoami)
    HOME_DIR=$HOME
    
    # Configure service file
    SERVICE_FILE="$SCRIPT_DIR/service/bird_cam.service"
    sed -e "s|%USER%|${CURRENT_USER}|g" \
        -e "s|%HOME%|${HOME_DIR}|g" \
        "${SERVICE_FILE}" > "${SERVICE_FILE}.tmp"
    mv "${SERVICE_FILE}.tmp" "${SERVICE_FILE}"
    
    echo "Service configured for user: $CURRENT_USER"
    echo "Home directory set to: $HOME_DIR"
else
    echo "Warning: Service file not found."
fi

# Step 5: Create data directories
echo
echo "Step 5: Creating data directories..."
mkdir -p "$PROJECT_ROOT/data/photos"

echo
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo
echo "To run the system manually:"
echo "  python3 $PROJECT_ROOT/bird_cam.py"
echo
echo "To install as a service:"
echo "  sudo cp $SCRIPT_DIR/service/bird_cam.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable bird_cam"
echo "  sudo systemctl start bird_cam"
echo
echo "Or simply run: make install-service"
echo
echo "For more information, see the README.md file." 