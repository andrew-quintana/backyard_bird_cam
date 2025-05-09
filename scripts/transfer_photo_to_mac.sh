#!/bin/bash
#
# Transfer the most recent bird photo to Mac
# 
# Usage: ./transfer_photo_to_mac.sh USERNAME IP_ADDRESS [PHOTOS_DIR]
# Example: ./transfer_photo_to_mac.sh your_username YOUR_MAC_IP ~/path/to/photos
#
# Setup:
# 1. Make script executable: chmod +x transfer_photo_to_mac.sh
# 2. Set up SSH keys between Pi and Mac for passwordless login
# 3. Run on Pi to transfer the most recent photo to your Mac
#

# Get parameters from command line
MAC_USERNAME="$1"
MAC_IP="$2"
PHOTOS_DIR="${3:-~/backyard_bird_cam/data/photos}"  # Use provided directory or default
MAC_DEST_DIR="~/1Projects/bird_cam/data/remote_photos"  # Destination directory on Mac

# Check if required parameters are provided
if [ -z "$MAC_USERNAME" ] || [ -z "$MAC_IP" ]; then
    echo "Error: Missing required parameters"
    echo "Usage: $0 USERNAME IP_ADDRESS [PHOTOS_DIR]"
    echo "  PHOTOS_DIR defaults to ~/backyard_bird_cam/data/photos if not specified"
    exit 1
fi

# Ensure destination directory exists on Mac
ssh "${MAC_USERNAME}@${MAC_IP}" "mkdir -p ${MAC_DEST_DIR}"

# Find the most recent photo
echo "Finding the most recent bird photo in ${PHOTOS_DIR}..."
RECENT_PHOTO=$(find "${PHOTOS_DIR}" -name "*.jpg" -type f -printf "%T@ %p\n" | sort -rn | head -n 1 | cut -d' ' -f2-)

# Check if we found any photos
if [ -z "${RECENT_PHOTO}" ]; then
    echo "No photos found in ${PHOTOS_DIR}"
    exit 1
fi

# Get the filename for transfer
FILENAME=$(basename "${RECENT_PHOTO}")

# Transfer the photo to the Mac
echo "Transferring photo to Mac (${MAC_USERNAME}@${MAC_IP})..."
if scp "${RECENT_PHOTO}" "${MAC_USERNAME}@${MAC_IP}:${MAC_DEST_DIR}/${FILENAME}"; then
    echo "Photo successfully transferred to your Mac: ${FILENAME}"
    echo "Location: ${MAC_DEST_DIR}/${FILENAME}"
else
    echo "Error: Failed to transfer photo. Please check your network and SSH configuration."
    exit 1
fi 