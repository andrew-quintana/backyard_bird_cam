#!/bin/bash

# Get current user
CURRENT_USER=$(whoami)

# Setup permissions
echo "Setting up permissions..."
sudo usermod -a -G gpio $CURRENT_USER
sudo usermod -a -G video $CURRENT_USER

# Create log files
echo "Creating log files..."
sudo touch /var/log/pigpiod.log /var/log/pigpiod.error.log
sudo touch /var/log/backyard_bird_cam.log /var/log/backyard_bird_cam.error.log
sudo chown $CURRENT_USER:gpio /var/log/pigpiod.log /var/log/pigpiod.error.log
sudo chown $CURRENT_USER:gpio /var/log/backyard_bird_cam.log /var/log/backyard_bird_cam.error.log
sudo chmod 664 /var/log/pigpiod.log /var/log/pigpiod.error.log
sudo chmod 664 /var/log/backyard_bird_cam.log /var/log/backyard_bird_cam.error.log

# Stop any running services
echo "Stopping existing services..."
sudo systemctl stop backyard_bird_cam@$CURRENT_USER.service
sudo systemctl stop pigpiod@$CURRENT_USER.service

# Install services
echo "Installing services..."
sudo cp scripts/service/pigpiod.service /etc/systemd/system/
sudo cp scripts/service/backyard_bird_cam.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start services
echo "Starting services..."
sudo systemctl enable pigpiod@$CURRENT_USER.service
sudo systemctl enable backyard_bird_cam@$CURRENT_USER.service
sudo systemctl start pigpiod@$CURRENT_USER.service
sudo systemctl start backyard_bird_cam@$CURRENT_USER.service

# Show status
echo "Service status:"
sudo systemctl status pigpiod@$CURRENT_USER.service
sudo systemctl status backyard_bird_cam@$CURRENT_USER.service

# Show logs
echo "Showing live logs (Ctrl+C to exit)..."
sudo journalctl -u pigpiod@$CURRENT_USER.service -u backyard_bird_cam@$CURRENT_USER.service -f

echo "Services installed and started for user: ${CURRENT_USER}"
echo "To check pigpiod status: sudo systemctl status pigpiod@${CURRENT_USER}.service"
echo "To check camera status: sudo systemctl status backyard_bird_cam@${CURRENT_USER}.service"
echo "To view camera logs: sudo journalctl -u backyard_bird_cam@${CURRENT_USER}.service -f" 