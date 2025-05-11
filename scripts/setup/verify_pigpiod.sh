#!/bin/bash

# Function to check if pigpiod is running
check_pigpiod() {
    if pgrep pigpiod > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if we can connect to pigpiod
check_connection() {
    python3 -c "
import pigpio
pi = pigpio.pi()
if pi.connected:
    print('Successfully connected to pigpiod')
    pi.stop()
    exit(0)
else:
    print('Failed to connect to pigpiod')
    exit(1)
"
}

echo "Checking pigpiod status..."

# First, stop any existing pigpiod processes
sudo killall pigpiod 2>/dev/null
sleep 2

# Start pigpiod with verbose output
echo "Starting pigpiod..."
sudo pigpiod -v

# Wait for it to start
sleep 2

# Check if it's running
if check_pigpiod; then
    echo "pigpiod process is running"
else
    echo "Failed to start pigpiod process"
    exit 1
fi

# Check if we can connect to it
if check_connection; then
    echo "pigpiod is working correctly"
    exit 0
else
    echo "pigpiod is running but not responding"
    exit 1
fi 