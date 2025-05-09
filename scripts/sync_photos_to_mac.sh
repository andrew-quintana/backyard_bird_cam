#!/bin/bash
#
# Sync all bird photos from Pi to Mac and delete originals
# 
# Usage: ./sync_photos_to_mac.sh USERNAME IP_ADDRESS [PHOTOS_DIR]
# Example: ./sync_photos_to_mac.sh your_username YOUR_MAC_IP ~/path/to/photos
#
# Setup:
# 1. Make script executable: chmod +x sync_photos_to_mac.sh
# 2. Set up SSH keys between Pi and Mac for passwordless login
# 3. Run on Pi to sync all photos to your Mac
#

# Get parameters from command line
MAC_USERNAME="$1"
MAC_IP="$2"
PHOTOS_DIR="${3:-/home/$(whoami)/bird_cam/data/photos}"  # Use provided directory or default
MAC_DEST_DIR="~/1Projects/bird_cam/data/remote_photos"  # Destination directory on Mac

# Check if required parameters are provided
if [ -z "$MAC_USERNAME" ] || [ -z "$MAC_IP" ]; then
    echo "Error: Missing required parameters"
    echo "Usage: $0 USERNAME IP_ADDRESS [PHOTOS_DIR]"
    echo "  PHOTOS_DIR defaults to /home/$(whoami)/bird_cam/data/photos if not specified"
    exit 1
fi

# Check if source directory exists
if [ ! -d "${PHOTOS_DIR}" ]; then
    echo "Error: Photos directory not found: ${PHOTOS_DIR}"
    exit 1
fi

# Count photos
PHOTO_COUNT=$(find "${PHOTOS_DIR}" -name "*.jpg" | wc -l)
if [ "${PHOTO_COUNT}" -eq 0 ]; then
    echo "No photos found in ${PHOTOS_DIR}"
    exit 0
fi

# Ensure destination directory exists on Mac
echo "Creating destination directory on Mac if needed..."
ssh "${MAC_USERNAME}@${MAC_IP}" "mkdir -p ${MAC_DEST_DIR}"

# Transfer all photos to the Mac
echo "Syncing ${PHOTO_COUNT} photos from ${PHOTOS_DIR} to Mac (${MAC_USERNAME}@${MAC_IP})..."
if rsync -avz --progress "${PHOTOS_DIR}/"*.jpg "${MAC_USERNAME}@${MAC_IP}:${MAC_DEST_DIR}/"; then
    echo "Photos successfully synced to your Mac"
    echo "Location: ${MAC_DEST_DIR}/"
    
    # Delete all jpg files after successful transfer
    echo "Deleting original photos from ${PHOTOS_DIR}..."
    find "${PHOTOS_DIR}" -name "*.jpg" -type f -delete
    DELETED_COUNT=$(echo $?)
    
    if [ $DELETED_COUNT -eq 0 ]; then
        echo "All photos successfully deleted from source directory"
    else
        echo "Warning: There may have been issues deleting some photos"
    fi
else
    echo "Error: Failed to sync photos. Please check your network and SSH configuration."
    echo "No photos were deleted from source directory."
    exit 1
fi 