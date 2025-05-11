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

# Check if port 8888 is already in use
echo "Checking if port 8888 is available..."
if sudo netstat -tulpn 2>/dev/null | grep :8888 > /dev/null; then
    echo "WARNING: Port 8888 is already in use!"
    sudo netstat -tulpn 2>/dev/null | grep :8888
fi

# Check permissions
echo "Checking permissions..."
ls -l /dev/gpiomem 2>/dev/null || echo "WARNING: /dev/gpiomem does not exist"
groups $USER | grep -q gpio && echo "User is in gpio group" || echo "WARNING: User is not in gpio group"

# Start pigpiod with verbose output and log to file
echo "Starting pigpiod..."
sudo pigpiod -v > /tmp/pigpiod.log 2>&1
PIGPID=$!

# Wait for it to start
sleep 2

# Check if it's running
if check_pigpiod; then
    echo "pigpiod process is running (PID: $PIGPID)"
    # Check if it's listening on port 8888
    if sudo netstat -tulpn 2>/dev/null | grep :8888 > /dev/null; then
        echo "pigpiod is listening on port 8888"
    else
        echo "WARNING: pigpiod is not listening on port 8888!"
        echo "Checking pigpiod logs:"
        cat /tmp/pigpiod.log
    fi
else
    echo "Failed to start pigpiod process"
    echo "Checking pigpiod logs:"
    cat /tmp/pigpiod.log
    exit 1
fi

# Check if we can connect to it
if check_connection; then
    echo "pigpiod is working correctly"
    exit 0
else
    echo "pigpiod is running but not responding"
    # Try to get more information about the process
    echo "Process details:"
    ps aux | grep pigpiod | grep -v grep
    echo "Port status:"
    sudo netstat -tulpn 2>/dev/null | grep :8888 || echo "No process listening on port 8888"
    echo "Checking pigpiod logs:"
    cat /tmp/pigpiod.log
    exit 1
fi 