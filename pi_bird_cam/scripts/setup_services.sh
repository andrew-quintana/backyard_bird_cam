#!/bin/bash

# Exit on any error
set -e

echo "Setting up bird camera services..."

# Get the current user and home directory
CURRENT_USER=$(whoami)
CURRENT_HOME=$(eval echo ~$CURRENT_USER)
echo "Current user: $CURRENT_USER"
echo "Home directory: $CURRENT_HOME"

# Verify directory structure
echo "Checking directory structure..."
if [ ! -d "$CURRENT_HOME/backyard_bird_cam" ]; then
    echo "Creating backyard_bird_cam directory in $CURRENT_HOME..."
    mkdir -p "$CURRENT_HOME/backyard_bird_cam"
fi

# Create logs directory
echo "Setting up logs directory..."
mkdir -p "$CURRENT_HOME/backyard_bird_cam/logs"
touch "$CURRENT_HOME/backyard_bird_cam/logs/camera.log" "$CURRENT_HOME/backyard_bird_cam/logs/camera.error.log"
chmod 644 "$CURRENT_HOME/backyard_bird_cam/logs/camera.log" "$CURRENT_HOME/backyard_bird_cam/logs/camera.error.log"

# Verify script exists
SCRIPT_PATH="$CURRENT_HOME/backyard_bird_cam/scripts/simple_pir_trigger.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi
echo "Found script at: $SCRIPT_PATH"

# Remove any custom pigpiod service to use system default
if [ -f /etc/systemd/system/pigpiod.service ]; then
    echo "Removing custom pigpiod service..."
    sudo rm /etc/systemd/system/pigpiod.service
fi

# Copy bird-camera service
echo "Installing bird-camera service..."
sudo cp "$(dirname "$0")/../services/bird-camera@.service" /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start services
echo "Enabling and starting services..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl enable bird-camera@$CURRENT_USER
sudo systemctl start bird-camera@$CURRENT_USER

echo "Services setup complete!"
echo "Checking service status..."
sudo systemctl status pigpiod bird-camera@$CURRENT_USER

echo -e "\nTo monitor the camera service in real-time, you can use any of these commands:"
echo "1. View all logs (including systemd messages):"
echo "   sudo journalctl -u bird-camera@$CURRENT_USER -f"
echo "2. View only the application output:"
echo "   tail -f $CURRENT_HOME/backyard_bird_cam/logs/camera.log"
echo "3. View only errors:"
echo "   tail -f $CURRENT_HOME/backyard_bird_cam/logs/camera.error.log"
echo -e "\nTo see the latest pictures taken:"
echo "   ls -ltr $CURRENT_HOME/backyard_bird_cam/images/" 