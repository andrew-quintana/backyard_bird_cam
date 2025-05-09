#!/bin/bash
# Transfer images from Raspberry Pi to local computer
# Usage: ./transfer_images.sh [pi_username] [pi_ip_address] [remote_path] [local_path]

# Default values
PI_USER=${1:-pi}
PI_IP=${2:-raspberrypi.local}
REMOTE_PATH=${3:-/home/pi/backyard_bird_cam/data/photos}
LOCAL_PATH=${4:-./data/remote_photos}

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_PATH"

# Print information
echo "Transferring images from Raspberry Pi"
echo "-------------------------------------"
echo "Pi address: $PI_USER@$PI_IP"
echo "Remote path: $REMOTE_PATH"
echo "Local path: $LOCAL_PATH"
echo

# First, get a list of files
echo "Getting list of image files..."
IMAGE_LIST=$(ssh $PI_USER@$PI_IP "ls -1 $REMOTE_PATH/*.jpg 2>/dev/null || echo 'No images found'")

# Check if any images were found
if [ "$IMAGE_LIST" = "No images found" ]; then
    echo "No images found on the Pi at $REMOTE_PATH"
    exit 0
fi

# Count the number of images
NUM_IMAGES=$(echo "$IMAGE_LIST" | wc -l)
echo "Found $NUM_IMAGES images on the Pi"

# Ask for confirmation
read -p "Transfer all these images? (y/n) " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Transfer canceled"
    exit 0
fi

# Transfer the files
echo "Transferring images..."
scp "$PI_USER@$PI_IP:$REMOTE_PATH/*.jpg" "$LOCAL_PATH/"

# Check if transfer was successful
if [ $? -eq 0 ]; then
    echo "Images successfully transferred to $LOCAL_PATH"
    
    # Count the number of transferred images
    TRANSFERRED=$(ls -1 $LOCAL_PATH/*.jpg 2>/dev/null | wc -l)
    echo "Transferred $TRANSFERRED images"
    
    # Ask if user wants to view the images
    read -p "Open the folder containing the images? (y/n) " VIEW
    if [[ "$VIEW" == "y" || "$VIEW" == "Y" ]]; then
        # Open folder based on OS
        case "$(uname)" in
            "Darwin") open "$LOCAL_PATH" ;;  # macOS
            "Linux") xdg-open "$LOCAL_PATH" ;;  # Linux
            "MINGW"*|"MSYS"*) explorer "$LOCAL_PATH" ;;  # Windows
            *) echo "Cannot open folder automatically on this OS" ;;
        esac
    fi
else
    echo "Error transferring images"
fi 