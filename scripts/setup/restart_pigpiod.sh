#!/bin/bash

# Stop any running pigpiod processes
sudo killall pigpiod 2>/dev/null
sleep 2

# Start pigpiod
sudo pigpiod

# Wait for pigpiod to be ready
sleep 2

# Check if pigpiod is running
if pgrep pigpiod > /dev/null; then
    echo "pigpiod started successfully"
else
    echo "Failed to start pigpiod"
    exit 1
fi 