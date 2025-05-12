#!/bin/bash

echo "Setting up bird camera services..."

# Get the actual user who ran sudo
ACTUAL_USER=$(logname)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo "Current user: $ACTUAL_USER"
echo "Home directory: $ACTUAL_HOME"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check directory structure
echo "Checking directory structure..."
if [ ! -d "$ACTUAL_HOME/backyard_bird_cam" ]; then
    echo "Error: backyard_bird_cam directory not found"
    exit 1
fi

# Set up permissions
echo "Setting up permissions..."
chmod 755 "$ACTUAL_HOME"
chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME"

chmod 777 "$ACTUAL_HOME/backyard_bird_cam"
chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/backyard_bird_cam"

# Create and set up logs directory
LOGS_DIR="$ACTUAL_HOME/backyard_bird_cam/logs"
mkdir -p "$LOGS_DIR"
chmod 777 "$LOGS_DIR"
chown $ACTUAL_USER:$ACTUAL_USER "$LOGS_DIR"

# Set permissions for all files except .env and virtual environments
find "$ACTUAL_HOME/backyard_bird_cam" -type f -not -path "*/\.*" -not -path "*/\.venv/*" -exec chmod 644 {} \;
find "$ACTUAL_HOME/backyard_bird_cam" -type d -not -path "*/\.*" -not -path "*/\.venv/*" -exec chmod 755 {} \;

# Set .env file permissions if it exists
if [ -f "$ACTUAL_HOME/backyard_bird_cam/.env" ]; then
    chmod 600 "$ACTUAL_HOME/backyard_bird_cam/.env"
    chown $ACTUAL_USER:$ACTUAL_USER "$ACTUAL_HOME/backyard_bird_cam/.env"
fi

# Verify script exists
SCRIPT_PATH="$ACTUAL_HOME/backyard_bird_cam/scripts/simple_pir_trigger.py"
if [ -f "$SCRIPT_PATH" ]; then
    echo "Found script at: $SCRIPT_PATH"
    chmod +x "$SCRIPT_PATH"
else
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Install service
echo "Installing bird-camera service..."
systemctl stop bird-camera@$ACTUAL_USER 2>/dev/null || true
systemctl disable bird-camera@$ACTUAL_USER 2>/dev/null || true

# Remove any custom pigpiod service
systemctl stop pigpiod 2>/dev/null || true
systemctl disable pigpiod 2>/dev/null || true

# Copy service file (using correct path)
SERVICE_FILE="$ACTUAL_HOME/backyard_bird_cam/pi_bird_cam/services/bird-camera@.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: Service file not found at $SERVICE_FILE"
    exit 1
fi
cp "$SERVICE_FILE" /etc/systemd/system/

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable and start services
echo "Enabling and starting services..."
systemctl enable pigpiod
systemctl start pigpiod
systemctl enable bird-camera@$ACTUAL_USER
systemctl start bird-camera@$ACTUAL_USER

echo "Services setup complete!"

# Check service status
echo "Checking service status..."
systemctl status pigpiod
systemctl status bird-camera@$ACTUAL_USER

echo -e "\nTo monitor the camera service in real-time, use:"
echo "   sudo journalctl -u bird-camera@$ACTUAL_USER -f"

echo -e "\nTo see the latest pictures taken:"
echo "   ls -ltr $ACTUAL_HOME/backyard_bird_cam/images/"

echo -e "\nTo view the application logs:"
echo "   tail -f $ACTUAL_HOME/backyard_bird_cam/logs/bird_camera_*.log" 