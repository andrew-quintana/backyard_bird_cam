#!/bin/bash

# Exit on any error
set -e

echo "Setting up bird camera services..."

# Remove any custom pigpiod service to use system default
if [ -f /etc/systemd/system/pigpiod.service ]; then
    echo "Removing custom pigpiod service..."
    sudo rm /etc/systemd/system/pigpiod.service
fi

# Copy bird-camera service
echo "Installing bird-camera service..."
sudo cp "$(dirname "$0")/../services/bird-camera.service" /etc/systemd/system/

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