# Bird Camera System Setup Guide

This guide explains how to set up and operate the automatic bird camera system.

## 1. System Overview

The bird camera system:
- Uses a PIR motion sensor to detect bird movement
- Captures 5 high-resolution photos in burst mode when motion is detected
- Transfers photos to your Mac computer
- Runs automatically on Raspberry Pi startup

## 2. Hardware Requirements

- Raspberry Pi (3, 4, or Zero 2W)
- Raspberry Pi Camera Module (v2 or HQ)
- PIR motion sensor
- Power supply (10000mAh battery or wall adapter)
- microSD card (16GB+ recommended)

## 3. Installation on Raspberry Pi

1. Copy all files to your Raspberry Pi:
   ```bash
   scp -r * pi@YOUR_PI_IP:/home/pi/bird_cam/
   ```

2. SSH into your Raspberry Pi:
   ```bash
   ssh pi@YOUR_PI_IP
   ```

3. Run the installation script:
   ```bash
   cd ~/bird_cam/scripts/setup
   chmod +x install_bird_cam.sh
   ./install_bird_cam.sh
   ```

4. Reboot the Raspberry Pi:
   ```bash
   sudo reboot
   ```

## 4. System Operation

### Automatic Operation

After installation and reboot, the system:
- Starts automatically on boot
- Detects motion and captures burst photos
- Saves photos to `/home/pi/bird_cam/data/photos`

### Manual Control

- Start: `sudo systemctl start bird_camera.service`
- Stop: `sudo systemctl stop bird_camera.service`
- Check status: `sudo systemctl status bird_camera.service`
- View logs: `sudo journalctl -u bird_camera.service -f`
- Disable autostart: `sudo systemctl disable bird_camera.service`

### Camera Parameters

The system uses these optimized parameters:
- 5 photos per burst
- 0.05 second sampling rate (fast response)
- 0.3 second delay between burst photos
- 3 second cooldown between motion triggers

To change these parameters, edit `scripts/launch_bird_cam.sh`.

## 5. Photo Management

### Viewing Photos

Connect to your Raspberry Pi with SFTP to browse and download photos.

### Auto-Transfer to Mac

To automatically transfer photos to your Mac:

1. Make sure your Mac is on the same network
2. Set up SSH keys for passwordless login
3. From the Pi, run:
   ```bash
   ~/bird_cam/scripts/sync_photos_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP
   ```

This will:
- Transfer all photos to your Mac
- Delete originals from the Pi to save space

### Automatic Transfers

To set up automatic transfers every 30 minutes, add this to crontab:
```
*/30 * * * * /home/pi/bird_cam/scripts/sync_photos_to_mac.sh YOUR_MAC_USERNAME YOUR_MAC_IP >> /home/pi/bird_cam/logs/sync.log 2>&1
```

## 6. Troubleshooting

### Camera Issues
- Camera not working: `vcgencmd get_camera` should show `supported=1 detected=1`
- Black images: Check camera ribbon cable connection

### Motion Detection Issues
- No detection: Check PIR sensor wiring (default GPIO4)
- Too sensitive: Adjust PIR sensor potentiometer

### Power Issues
- System crashes: Ensure adequate power (use 5V/2.5A+ supply)
- Battery drains quickly: Consider reducing resolution or sampling rate

## 7. Customization

### Change Photo Resolution

Edit `scripts/simple_pir_trigger.py` to adjust the resolution in `initialize_camera()`.

### Change PIR Pin

To use a different GPIO pin for the PIR sensor, add `--pin X` to the command in `launch_bird_cam.sh` (replace X with GPIO pin number).

### Other Parameters

All configurable options in `simple_pir_trigger.py` can be set in `launch_bird_cam.sh`. 