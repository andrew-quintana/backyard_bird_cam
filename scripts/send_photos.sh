#!/bin/bash
# Send photos from Raspberry Pi to a remote computer
# Run this script ON THE PI to send photos TO your Mac/PC
# Usage: ./send_photos.sh [remote_username] [remote_ip] [remote_directory]

# Default values
REMOTE_USER=${1:-aq_home}
REMOTE_IP=${2:-192.168.5.144}  # Change this to your Mac's IP
REMOTE_DIR=${3:-"1Projects/bird_cam/data/remote_photos"}
LOCAL_PHOTOS_DIR="$HOME/backyard_bird_cam/data/photos"

# Print information
echo "Sending photos to remote computer"
echo "--------------------------------"
echo "From Pi: $LOCAL_PHOTOS_DIR"
echo "To: $REMOTE_USER@$REMOTE_IP:$REMOTE_DIR"
echo

# Check if photos directory exists
if [ ! -d "$LOCAL_PHOTOS_DIR" ]; then
    echo "Error: Photos directory does not exist: $LOCAL_PHOTOS_DIR"
    exit 1
fi

# Count photos
PHOTO_COUNT=$(ls -1 "$LOCAL_PHOTOS_DIR"/*.jpg 2>/dev/null | wc -l)

if [ "$PHOTO_COUNT" -eq 0 ]; then
    echo "No photos found in $LOCAL_PHOTOS_DIR"
    exit 0
fi

echo "Found $PHOTO_COUNT photos to send"

# Ask for confirmation
read -p "Send these photos? (y/n) " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Sending canceled"
    exit 0
fi

# Ensure remote directory exists
ssh $REMOTE_USER@$REMOTE_IP "mkdir -p $REMOTE_DIR"

if [ $? -ne 0 ]; then
    echo "Error: Could not create remote directory. Check your permissions and SSH setup."
    exit 1
fi

# Send the files
echo "Sending photos..."
scp "$LOCAL_PHOTOS_DIR"/*.jpg "$REMOTE_USER@$REMOTE_IP:$REMOTE_DIR/"

# Check if transfer was successful
if [ $? -eq 0 ]; then
    echo "Photos successfully sent to $REMOTE_USER@$REMOTE_IP:$REMOTE_DIR"
    
    # Ask if user wants to delete the local copies
    read -p "Delete local copies of the photos? (y/n) " DELETE
    if [[ "$DELETE" == "y" || "$DELETE" == "Y" ]]; then
        echo "Deleting local copies..."
        rm "$LOCAL_PHOTOS_DIR"/*.jpg
        echo "Local copies deleted."
    fi
else
    echo "Error sending photos"
fi 