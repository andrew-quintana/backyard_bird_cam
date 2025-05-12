#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if we're in the correct directory
if [ ! -d "$SCRIPT_DIR/pi_bird_cam" ]; then
    echo "Error: Cannot find pi_bird_cam directory"
    echo "Please run this script from the backyard_bird_cam directory"
    exit 1
fi

# Run the actual script with all arguments passed to this wrapper
"$SCRIPT_DIR/pi_bird_cam/scripts/transfer_pictures.sh" "$@" 