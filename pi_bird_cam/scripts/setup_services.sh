#!/bin/bash

# Exit on any error
set -e

echo "Setting up bird camera services..."

# Get the current user
CURRENT_USER=$(whoami)
echo "Setting up services for user: $CURRENT_USER"

# Ensure the backyard_bird_cam directory exists in the user's home
if [ ! -d "$HOME/backyard_bird_cam" ]; then
    echo "Creating backyard_bird_cam directory in $HOME..."
    mkdir -p "$HOME/backyard_bird_cam"
fi

# Remove any custom pigpiod service to use system default
if [ -f /etc/systemd/system/pigpiod.service ]; then
    echo "Removing custom pigpiod service..."
    sudo rm /etc/systemd/system/pigpiod.service
fi

# Copy bird-camera service
echo "Installing bird-camera service..."
sudo cp "$(dirname "$0")/../services/bird-camera.service" /etc/systemd/system/

# Create log files with proper permissions
echo "Setting up log files..."
sudo touch /var/log/bird-camera.log /var/log/bird-camera.error.log
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/bird-camera.log /var/log/bird-camera.error.log

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start services
echo "Enabling and starting services..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl enable bird-camera
sudo systemctl start bird-camera

echo "Services setup complete!"
echo "You can check status with: sudo systemctl status pigpiod bird-camera" 