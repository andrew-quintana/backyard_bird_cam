#!/bin/bash

# Function to display usage
show_usage() {
    echo "Usage: $0 <username> <ip_address> <target_directory> [--delete]"
    echo ""
    echo "Arguments:"
    echo "  username          : Username on the target computer"
    echo "  ip_address        : IP address of the target computer"
    echo "  target_directory  : Directory on target computer to store pictures"
    echo "  --delete         : Optional flag to delete local files after transfer"
    echo ""
    echo "Example:"
    echo "  $0 john 192.168.1.100 /home/john/Pictures/bird_cam --delete"
}

# Check if help is requested
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_usage
    exit 0
fi

# Check if we have the minimum required arguments
if [ $# -lt 3 ]; then
    echo "Error: Missing required arguments"
    show_usage
    exit 1
fi

# Parse arguments
USERNAME=$1
IP_ADDRESS=$2
TARGET_DIR=$3
DELETE_FILES=false

# Check for delete flag
if [ "$4" == "--delete" ]; then
    DELETE_FILES=true
fi

# Get the actual user who ran the script
ACTUAL_USER=$(logname)
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

# Source directory for pictures
SOURCE_DIR="$ACTUAL_HOME/backyard_bird_cam/data/photos"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist"
    exit 1
fi

# Check if there are any pictures to transfer
if [ -z "$(ls -A $SOURCE_DIR)" ]; then
    echo "No pictures found in $SOURCE_DIR"
    exit 0
fi

echo "Starting picture transfer..."
echo "From: $SOURCE_DIR"
echo "To: $USERNAME@$IP_ADDRESS:$TARGET_DIR"

# Create target directory if it doesn't exist
ssh $USERNAME@$IP_ADDRESS "mkdir -p $TARGET_DIR"

# Transfer files
echo "Transferring files..."
scp -r "$SOURCE_DIR"/* $USERNAME@$IP_ADDRESS:$TARGET_DIR/

# Check if transfer was successful
if [ $? -eq 0 ]; then
    echo "Transfer completed successfully!"
    
    # Delete local files if requested
    if [ "$DELETE_FILES" = true ]; then
        echo "Deleting local files..."
        rm -f "$SOURCE_DIR"/*
        echo "Local files deleted"
    fi
else
    echo "Error: Transfer failed"
    exit 1
fi

echo "Done!" 