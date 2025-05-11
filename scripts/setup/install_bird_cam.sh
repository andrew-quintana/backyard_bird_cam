#!/bin/bash
#
# Bird Camera System Installation Script
#
# This script installs all necessary components and 
# configures the bird camera to start on boot
#

# Exit on error
set -e

echo "===================================================="
echo "  Bird Camera System Installation"
echo "===================================================="
echo

# Install required packages
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-picamera2 pigpio python3-pigpio

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install RPi.GPIO argparse

# Enable and start pigpiod daemon
echo "Enabling pigpio daemon..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Make scripts executable
echo "Setting permissions..."
chmod +x $(dirname "$0")/../launch_bird_cam.sh

# Install service for autostart
echo "Installing systemd service..."
sudo cp $(dirname "$0")/../service/bird_camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bird_camera.service

echo
echo "Creating data directory..."
mkdir -p ~/bird_cam/data/photos

echo
echo "===================================================="
echo "  Installation Complete!"
echo "===================================================="
echo
echo "To start the camera system now, run:"
echo "  sudo systemctl start bird_camera.service"
echo 
echo "To check status:"
echo "  sudo systemctl status bird_camera.service"
echo
echo "To view logs:"
echo "  sudo journalctl -u bird_camera.service -f"
echo
echo "Camera will automatically start on next boot."
echo "Photos will be saved to ~/bird_cam/data/photos"
echo "====================================================" 