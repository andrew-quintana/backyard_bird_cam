#!/bin/bash
# Script to update the camera handler with improved code for better memory handling

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Backup the original file
CAMERA_HANDLER_PATH="$PROJECT_ROOT/src/camera/camera_handler.py"
BACKUP_PATH="$CAMERA_HANDLER_PATH.backup"

echo "Backing up original camera handler to $BACKUP_PATH"
cp "$CAMERA_HANDLER_PATH" "$BACKUP_PATH"

# Copy the improved version
echo "Updating camera handler with improved version"
cp "$SCRIPT_DIR/../src/camera/camera_handler.py.patch" "$CAMERA_HANDLER_PATH"

echo "Camera handler updated. Original backed up at $BACKUP_PATH" 