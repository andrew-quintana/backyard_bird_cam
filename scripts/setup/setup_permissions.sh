#!/bin/bash

# Get the current user
CURRENT_USER=$(whoami)

# Create gpio group if it doesn't exist
sudo groupadd -f gpio

# Add user to gpio group
sudo usermod -a -G gpio $CURRENT_USER

# Set up udev rules for GPIO
echo 'SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"' | sudo tee /etc/udev/rules.d/90-gpio.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Permissions set up for user: $CURRENT_USER"
echo "You may need to log out and log back in for group changes to take effect"
echo "Or run 'newgrp gpio' to apply changes in current session" 