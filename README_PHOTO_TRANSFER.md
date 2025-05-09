# Bird Camera Photo Transfer Guide

This guide explains how to transfer bird camera photos from your Raspberry Pi to your Mac.

## Option 1: Transfer Most Recent Photo

Use this option to quickly transfer just the most recent photo:

1. On your Mac, find your IP address:
   ```
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   Note your IP address

2. Transfer the script to your Pi:
   ```
   scp scripts/transfer_photo_to_mac.sh pi@YOUR_PI_IP:/home/pi/bird_cam/scripts/
   ```

3. SSH into your Pi:
   ```
   ssh pi@YOUR_PI_IP
   ```

4. Make the script executable:
   ```
   cd ~/bird_cam/scripts
   chmod +x transfer_photo_to_mac.sh
   ```

5. Run the script with your Mac's username and IP address:
   ```
   ./transfer_photo_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP
   ```
   
   You can also specify a custom photos directory:
   ```
   ./transfer_photo_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP /path/to/your/photos
   ```

The most recent photo will be transferred to your Mac in the directory configured in the script (`~/1Projects/bird_cam/data/remote_photos` by default).

## Option 2: Sync All Photos

Use this option to transfer all photos from your Pi to your Mac:

1. On your Mac, find your IP address (as above)

2. Transfer the script to your Pi:
   ```
   scp scripts/sync_photos_to_mac.sh pi@YOUR_PI_IP:/home/pi/bird_cam/scripts/
   ```

3. SSH into your Pi

4. Make the script executable:
   ```
   cd ~/bird_cam/scripts
   chmod +x sync_photos_to_mac.sh
   ```

5. Run the script with your Mac's username and IP address:
   ```
   ./sync_photos_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP
   ```
   
   You can also specify a custom photos directory:
   ```
   ./sync_photos_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP /path/to/your/photos
   ```

All photos will be transferred to your Mac in the directory configured in the script (`~/1Projects/bird_cam/data/remote_photos` by default).

## Customizing the Destination

If you want to change where photos are stored on your Mac:

1. Edit the script and modify the `MAC_DEST_DIR` variable:
   ```
   nano transfer_photo_to_mac.sh
   ```
   or
   ```
   nano sync_photos_to_mac.sh
   ```

2. Change this line to your preferred location:
   ```
   MAC_DEST_DIR="~/1Projects/bird_cam/data/remote_photos"
   ```

## Setting Up SSH Keys (Optional but Recommended)

For passwordless transfers:

1. On your Pi, generate SSH keys if you haven't already:
   ```
   ssh-keygen -t rsa
   ```

2. Copy the key to your Mac:
   ```
   ssh-copy-id YOUR_MAC_USERNAME@YOUR_MAC_IP
   ```

3. Test the connection:
   ```
   ssh YOUR_MAC_USERNAME@YOUR_MAC_IP
   ```

You should now be able to connect without entering a password.

## Scheduling Automatic Transfers

To automatically sync photos every hour, add a cron job on your Pi:

```
crontab -e
```

Add this line:
```
0 * * * * /home/pi/bird_cam/scripts/sync_photos_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP /path/to/photos >> /home/pi/bird_cam/logs/photo_sync.log 2>&1
```

This will run the sync script every hour and log the results. 