#!/bin/bash
# Script to check the status of the Bird Camera system

echo "=========================================="
echo "Bird Camera System Status"
echo "=========================================="
echo

# Check if pigpiod is running
echo "Checking pigpio daemon status:"
if systemctl is-active pigpiod > /dev/null 2>&1; then
    echo "✅ pigpiod service is running"
else
    echo "❌ pigpiod service is NOT running"
    echo "   Run: sudo systemctl start pigpiod"
fi
echo

# Check if bird_cam service is installed and running
echo "Checking bird_cam service status:"
if [ -f /etc/systemd/system/bird_cam.service ]; then
    echo "✅ Service is installed"
    
    if systemctl is-active bird_cam > /dev/null 2>&1; then
        echo "✅ Service is running"
    else
        echo "❌ Service is NOT running"
        echo "   Run: sudo systemctl start bird_cam"
    fi
    
    if systemctl is-enabled bird_cam > /dev/null 2>&1; then
        echo "✅ Service is enabled at boot"
    else
        echo "❌ Service is NOT enabled at boot"
        echo "   Run: sudo systemctl enable bird_cam"
    fi
else
    echo "❌ Service is NOT installed"
    echo "   Run: make install-service"
fi
echo

# Check if camera is available
echo "Checking camera status:"
if vcgencmd get_camera | grep "detected=1" > /dev/null; then
    echo "✅ Camera is detected"
else
    echo "❌ Camera is NOT detected"
    echo "   Check camera connection and enable camera in raspi-config"
fi
echo

# Check for data directory and photos
PHOTO_DIR="data/photos"
echo "Checking data directories:"
if [ -d "$PHOTO_DIR" ]; then
    PHOTO_COUNT=$(ls -1 "$PHOTO_DIR"/*.jpg 2>/dev/null | wc -l)
    echo "✅ Photo directory exists"
    echo "   $PHOTO_COUNT photos stored"
else
    echo "❌ Photo directory does NOT exist"
    echo "   Run: mkdir -p $PHOTO_DIR"
fi
echo

# Display system info
echo "System information:"
uptime
echo
free -h
echo
df -h | grep /dev/root

echo
echo "To view recent logs:"
echo "  sudo journalctl -u bird_cam -n 20" 