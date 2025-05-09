#!/bin/bash
# Find image files on the Raspberry Pi
# Usage: ./find_images.sh [username] [pi_ip_address]

# Default values
PI_USER=${1:-pi}
PI_IP=${2:-raspberrypi.local}

echo "Looking for images on Raspberry Pi ($PI_USER@$PI_IP)..."
echo "------------------------------------------------------"

# Check the most likely directories first
echo "Checking project directories:"
ssh $PI_USER@$PI_IP "find ~/backyard_bird_cam -name '*.jpg' | head -20"

echo -e "\nChecking current directory:"
ssh $PI_USER@$PI_IP "find ~/. -maxdepth 2 -name '*.jpg' | head -20"

echo -e "\nSearch for recently modified image files (last 24 hours):"
ssh $PI_USER@$PI_IP "find ~/ -name '*.jpg' -mtime -1 | head -20"

echo -e "\nSearch for any JPG files in home directory structure:"
ssh $PI_USER@$PI_IP "find ~/ -name '*.jpg' -type f | grep -v '/.local/' | grep -v '/.cache/' | head -20" 