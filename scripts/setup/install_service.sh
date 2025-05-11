#!/bin/bash

# Get the current user
CURRENT_USER=$(whoami)

# Set up permissions
echo "Setting up permissions..."
"$(dirname "$0")/setup_permissions.sh"

# Apply group changes in current session
echo "Applying group changes..."
newgrp gpio

# Install pigpiod service
echo "Installing pigpiod service..."
sudo cp "$(dirname "$0")/../service/pigpiod.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service

# Install backyard_bird_cam service
echo "Installing backyard_bird_cam service..."
sudo cp "$(dirname "$0")/../service/backyard_bird_cam.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable backyard_bird_cam@$CURRENT_USER.service
sudo systemctl start backyard_bird_cam@$CURRENT_USER.service

# Show status
echo "Service status:"
sudo systemctl status pigpiod.service
sudo systemctl status backyard_bird_cam@$CURRENT_USER.service

echo "Services installed and started for user: ${CURRENT_USER}"
echo "To check pigpiod status: sudo systemctl status pigpiod.service"
echo "To check camera status: sudo systemctl status backyard_bird_cam@${CURRENT_USER}.service"
echo "To view camera logs: sudo journalctl -u backyard_bird_cam@${CURRENT_USER}.service -f" 