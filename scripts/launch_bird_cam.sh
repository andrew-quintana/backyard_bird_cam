#!/bin/bash
#
# Bird Camera System Launcher
# 
# This script launches the bird camera with optimal parameters
# Install location: /home/pi/bird_cam/scripts/
#

# Navigate to the bird_cam directory
cd "$(dirname "$0")/.."
BASE_DIR="$(pwd)"
SCRIPTS_DIR="${BASE_DIR}/scripts"
DATA_DIR="${BASE_DIR}/data/photos"

# Ensure data directory exists
mkdir -p "${DATA_DIR}"

# Check if pigpiod is running
if ! pgrep pigpiod > /dev/null; then
    echo "Starting pigpio daemon..."
    sudo pigpiod
    sleep 2
fi

# Kill any existing instances
pkill -f simple_pir_trigger.py

# Launch the camera system with optimal parameters
echo "Starting bird camera system..."
echo "Output directory: ${DATA_DIR}"
echo "Parameters: 5 burst photos, 0.05s sampling rate, 0.3s burst delay"

python3 "${SCRIPTS_DIR}/simple_pir_trigger.py" \
    --output "${DATA_DIR}" \
    --burst 5 \
    --sampling-rate 0.05 \
    --burst-delay 0.3 \
    --cooldown 3

# This script should never exit unless the Python program crashes
echo "Bird camera system stopped. Check logs for errors." 