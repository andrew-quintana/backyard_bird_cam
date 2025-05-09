# File Transfer Between Raspberry Pi and Your Computer

There are two ways to transfer photos between your Raspberry Pi and your computer. Each approach has its own script and use case.

## Option 1: Pull Photos FROM the Pi (Run on your Mac/PC)

Use the `transfer_images.sh` script when you want to run a command on your Mac/PC to download photos from the Pi.

```bash
# Run this ON YOUR MAC/PC
cd /Users/aq_home/1Projects/bird_cam
./scripts/transfer_images.sh fizz 192.168.5.144
```

This script:
- Is executed on your Mac/PC
- Connects to the Pi using SSH
- Pulls photos FROM the Pi TO your Mac/PC
- Requires SSH to be set up on your Pi
- Saves photos to your local `data/remote_photos` directory

## Option 2: Push Photos TO your Mac/PC (Run on the Pi)

Use the `send_photos.sh` script when you want to run a command on the Pi to upload photos to your Mac/PC.

```bash
# Run this ON THE PI
cd ~/backyard_bird_cam
./scripts/send_photos.sh aq_home 192.168.5.144
```

This script:
- Is executed on the Raspberry Pi
- Connects to your Mac/PC using SSH
- Pushes photos FROM the Pi TO your Mac/PC
- Requires SSH to be set up on your Mac/PC
- Gives the option to delete local copies after sending

## Requirements for Both Methods

### SSH Setup for Option 1 (transfer_images.sh)
1. The Pi must have SSH enabled
2. Your Mac/PC must have SSH key access to the Pi, or you must enter the Pi's password

### SSH Setup for Option 2 (send_photos.sh)
1. Your Mac/PC must have SSH enabled
2. The Pi must have SSH key access to your Mac/PC, or you must enter your Mac/PC's password
3. Your Mac/PC must allow incoming SSH connections (System Preferences → Sharing → Remote Login)

## Which Method to Use?

- **Option 1 (transfer_images.sh)**: Best when you want to manage everything from your Mac/PC
- **Option 2 (send_photos.sh)**: Best when the Pi is automatically taking photos and you want it to periodically send them to your computer

## Troubleshooting

### "Permission denied" or "No such file or directory"
- Check that the target directory exists
- Make sure you have permission to write to the destination
- For Option 2, ensure Remote Login is enabled on your Mac/PC

### SSH Authentication Issues
- Check that SSH keys are properly set up
- Try using the password method if key authentication fails

### Network Issues
- Ensure both devices are on the same network
- Check that you're using the correct IP address
- Make sure no firewall is blocking the connection 