#!/bin/bash

# Get the actual user who ran sudo
ACTUAL_USER=$(logname)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "Setting up bird camera services..."
echo "Current user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo"
    exit 1
fi

# Check if we have a valid user
if [ -z "$ACTUAL_USER" ]; then
    echo "Error: Could not determine the actual user"
    exit 1
fi

# Check if the user's home directory exists
if [ ! -d "$ACTUAL_HOME" ]; then
    echo "Error: Home directory $ACTUAL_HOME does not exist"
    exit 1
fi

# Check if the backyard_bird_cam directory exists
if [ ! -d "$ACTUAL_HOME/backyard_bird_cam" ]; then
    echo "Error: Directory $ACTUAL_HOME/backyard_bird_cam does not exist"
    exit 1
fi

echo "Checking directory structure..."
echo "Setting up permissions..."

# Set directory permissions
chmod 777 "$ACTUAL_HOME/backyard_bird_cam"

# Set ownership of files (excluding .env and virtual environments)
find "$ACTUAL_HOME/backyard_bird_cam" -type f -not -path "*/\.*" -not -path "*/\.venv/*" -not -path "*/venv/*" -exec chown $ACTUAL_USER:$ACTUAL_USER {} \;
find "$ACTUAL_HOME/backyard_bird_cam" -type d -not -path "*/\.*" -not -path "*/\.venv/*" -not -path "*/venv/*" -exec chown $ACTUAL_USER:$ACTUAL_USER {} \;

# Set permissions for .env file if it exists
if [ -f "$ACTUAL_HOME/backyard_bird_cam/.env" ]; then
    chmod 600 "$ACTUAL_HOME/backyard_bird_cam/.env"
    chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/backyard_bird_cam/.env"
fi

# Verify the script exists
SCRIPT_PATH="$ACTUAL_HOME/backyard_bird_cam/scripts/simple_pir_trigger.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

echo "Found script at: $SCRIPT_PATH"

# Make the script executable
chmod +x "$SCRIPT_PATH"

echo "Installing bird-camera service..."

# Remove any custom pigpiod service if it exists
if [ -f "/etc/systemd/system/pigpiod.service" ]; then
    systemctl stop pigpiod.service
    systemctl disable pigpiod.service
    rm /etc/systemd/system/pigpiod.service
fi

# Copy the service file
cp "$ACTUAL_HOME/backyard_bird_cam/pi_bird_cam/services/bird-camera@.service" /etc/systemd/system/

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling and starting services..."
systemctl enable pigpiod.service
systemctl start pigpiod.service
systemctl enable bird-camera@$ACTUAL_USER.service
systemctl start bird-camera@$ACTUAL_USER.service

echo "Services setup complete!"
echo "Checking service status..."
systemctl status pigpiod.service
systemctl status bird-camera@$ACTUAL_USER.service

echo -e "\nTo monitor the camera service in real-time, use:"
echo "   sudo journalctl -u bird-camera@$ACTUAL_USER -f"
echo -e "\nTo see the latest pictures taken:"
echo "   ls -ltr $ACTUAL_HOME/backyard_bird_cam/images/" 