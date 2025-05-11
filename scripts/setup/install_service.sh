#!/bin/bash

# Get the current user
CURRENT_USER=$(whoami)

# Install pigpiod service
sudo cp "$(dirname "$0")/../service/pigpiod.service" /etc/systemd/system/pigpiod.service
sudo systemctl daemon-reload
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service

# Install bird camera service
sudo cp "$(dirname "$0")/../service/backyard_bird_cam.service" /etc/systemd/system/backyard_bird_cam@${CURRENT_USER}.service
sudo systemctl daemon-reload
sudo systemctl enable backyard_bird_cam@${CURRENT_USER}.service
sudo systemctl start backyard_bird_cam@${CURRENT_USER}.service

echo "Services installed and started for user: ${CURRENT_USER}"
echo "To check pigpiod status: sudo systemctl status pigpiod.service"
echo "To check camera status: sudo systemctl status backyard_bird_cam@${CURRENT_USER}.service"
echo "To view camera logs: sudo journalctl -u backyard_bird_cam@${CURRENT_USER}.service -f" 