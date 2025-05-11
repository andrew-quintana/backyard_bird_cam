# Bird Camera Photo Transfer Guide

This guide explains how to transfer bird camera photos from your Raspberry Pi to your computer (Mac or Windows).

## Option 1: Transfer Most Recent Photo

Use this option to quickly transfer just the most recent photo.

### 1. Find Your Computer's IP Address

#### On Mac:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
#### On Windows (PowerShell):
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '127.*'}
```
Note your computer's IP address.

### 2. Transfer the Script to Your Pi

#### On Mac (Terminal):
```bash
scp scripts/transfer_photo_to_mac.sh pi@YOUR_PI_IP:/home/pi/bird_cam/scripts/
```
#### On Windows:
- Use [WinSCP](https://winscp.net/) or [OpenSSH for Windows](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse) to copy `scripts/transfer_photo_to_mac.sh` to `/home/pi/bird_cam/scripts/` on your Pi.

### 3. SSH into Your Pi

#### On Mac:
```bash
ssh pi@YOUR_PI_IP
```
#### On Windows:
- Use [PuTTY](https://www.putty.org/) or Windows Terminal:
```powershell
ssh pi@YOUR_PI_IP
```

### 4. Make the Script Executable
```bash
cd ~/bird_cam/scripts
chmod +x transfer_photo_to_mac.sh
```

### 5. Run the Script with Your Computer's Username and IP Address
```bash
./transfer_photo_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP
```
You can also specify a custom photos directory:
```bash
./transfer_photo_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP /path/to/your/photos
```

The most recent photo will be transferred to your computer in the directory configured in the script (by default: `~/1Projects/bird_cam/data/remote_photos` on Mac, or the equivalent path on Windows).

## Option 2: Sync All Photos

Use this option to transfer all photos from your Pi to your computer.

### 1. Find Your Computer's IP Address
- See step 1 above for Mac and Windows instructions.

### 2. Transfer the Script to Your Pi
- See step 2 above for Mac and Windows instructions, but use `sync_photos_to_mac.sh`.

### 3. SSH into Your Pi
- See step 3 above.

### 4. Make the Script Executable
```bash
cd ~/bird_cam/scripts
chmod +x sync_photos_to_mac.sh
```

### 5. Run the Script with Your Computer's Username and IP Address
```bash
./sync_photos_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP
```
You can also specify a custom photos directory:
```bash
./sync_photos_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP /path/to/your/photos
```

All photos will be transferred to your computer in the directory configured in the script (by default: `~/1Projects/bird_cam/data/remote_photos` on Mac, or the equivalent path on Windows).

## Customizing the Destination

If you want to change where photos are stored on your computer:

1. Edit the script and modify the `MAC_DEST_DIR` variable (works for both Mac and Windows if using OpenSSH):
```bash
nano transfer_photo_to_mac.sh
```
or
```bash
nano sync_photos_to_mac.sh
```
2. Change this line to your preferred location:
```bash
MAC_DEST_DIR="~/1Projects/bird_cam/data/remote_photos"
```
For Windows, use a path like `/c/Users/YOUR_USERNAME/Pictures/bird_photos` if using OpenSSH, or set your WinSCP destination folder.

## Setting Up SSH Keys (Optional but Recommended)

For passwordless transfers:

1. On your Pi, generate SSH keys if you haven't already:
```bash
ssh-keygen -t rsa
```
2. Copy the key to your computer:
```bash
ssh-copy-id YOUR_COMPUTER_USERNAME@YOUR_COMPUTER_IP
```
- On Windows, you may need to use [OpenSSH](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse) or manually copy the public key to `C:\Users\YOUR_USERNAME\.ssh\authorized_keys`.

3. Test the connection:
```bash
ssh YOUR_COMPUTER_USERNAME@YOUR_COMPUTER_IP
```

You should now be able to connect without entering a password.

## Scheduling Automatic Transfers

To automatically sync photos every hour, add a cron job on your Pi:

```bash
crontab -e
```
Add this line:
```bash
0 * * * * /home/pi/bird_cam/scripts/sync_photos_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP /path/to/photos >> /home/pi/bird_cam/logs/photo_sync.log 2>&1
```

This will run the sync script every hour and log the results.

## Notes for Windows Users
- You can use [WinSCP](https://winscp.net/) for a graphical interface to transfer files via SCP/SFTP.
- If using OpenSSH, you can use the same command-line instructions as Mac/Linux.
- Ensure your Windows firewall allows SSH connections.
- File paths may differ; use `/c/Users/YOUR_USERNAME/...` for OpenSSH or standard Windows paths in WinSCP. 