#!/bin/bash

# Get the current user
CURRENT_USER=$(whoami)

# Copy the service file to systemd directory
sudo cp "$(dirname "$0")/../service/backyard_bird_cam.service" /etc/systemd/system/backyard_bird_cam@${CURRENT_USER}.service

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service for the current user
sudo systemctl enable backyard_bird_cam@${CURRENT_USER}.service

# Start the service
sudo systemctl start backyard_bird_cam@${CURRENT_USER}.service

echo "Service installed and started for user: ${CURRENT_USER}"
echo "To check status: sudo systemctl status backyard_bird_cam@${CURRENT_USER}.service"
echo "To view logs: sudo journalctl -u backyard_bird_cam@${CURRENT_USER}.service -f" 