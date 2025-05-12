#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TRANSFER_SCRIPT="$SCRIPT_DIR/pi_bird_cam/scripts/transfer_pictures.sh"

# Check if the transfer script exists
if [ ! -f "$TRANSFER_SCRIPT" ]; then
    echo "Error: Cannot find transfer script at $TRANSFER_SCRIPT"
    echo "Please ensure you're running this from the backyard_bird_cam directory"
    exit 1
fi

# Check if the transfer script is executable
if [ ! -x "$TRANSFER_SCRIPT" ]; then
    echo "Error: Transfer script is not executable"
    echo "Attempting to fix permissions..."
    chmod +x "$TRANSFER_SCRIPT" || {
        echo "Failed to make script executable. Please run: chmod +x $TRANSFER_SCRIPT"
        exit 1
    }
fi

# Run the actual script with all arguments passed to this wrapper
"$TRANSFER_SCRIPT" "$@" 