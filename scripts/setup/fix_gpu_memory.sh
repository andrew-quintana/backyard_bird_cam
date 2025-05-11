#!/bin/bash

echo "Checking current GPU memory..."
vcgencmd get_mem gpu

echo "Checking for GPU throttling..."
vcgencmd get_throttled

echo "Checking current config.txt settings..."
if [ -f /boot/config.txt ]; then
    echo "Current GPU memory settings:"
    grep -i "gpu_mem" /boot/config.txt || echo "No GPU memory settings found"
else
    echo "WARNING: /boot/config.txt not found!"
    exit 1
fi

echo "Backing up config.txt..."
sudo cp /boot/config.txt /boot/config.txt.backup

echo "Updating GPU memory settings..."
# Remove any existing gpu_mem settings
sudo sed -i '/^gpu_mem/d' /boot/config.txt

# Add new settings
echo "gpu_mem=128" | sudo tee -a /boot/config.txt
echo "gpu_mem_256=128" | sudo tee -a /boot/config.txt
echo "gpu_mem_512=128" | sudo tee -a /boot/config.txt
echo "gpu_mem_1024=128" | sudo tee -a /boot/config.txt

echo "New config.txt settings:"
grep -i "gpu_mem" /boot/config.txt

echo "Please reboot your system to apply these changes:"
echo "sudo reboot" 