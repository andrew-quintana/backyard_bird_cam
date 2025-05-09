# Raspberry Pi Setup Guide

This guide will help you set up the bird camera system on your Raspberry Pi.

## Initial Setup

```bash
# SSH into your Pi
ssh pi@your_raspberry_pi_ip

# Clone the repository
git clone https://github.com/andrew-quintana/backyard_bird_cam.git ~/backyard_bird_cam

# Navigate to the project directory
cd ~/backyard_bird_cam

# Make sure scripts are executable
chmod +x scripts/*.py scripts/*.sh
```

## Install Dependencies

```bash
# Update package list
sudo apt-get update

# Install required packages
sudo apt-get install -y python3-pip python3-pigpio python3-pil

# Install Python requirements
pip3 install pigpio Pillow

# Start the pigpio daemon
sudo pigpiod

# To make pigpio start automatically on boot
sudo systemctl enable pigpiod
```

## Test the Camera

Take a test photo to ensure the camera is working correctly:

```bash
# Make sure you're in the project directory
cd ~/backyard_bird_cam

# Take a test photo (no PIR trigger)
./scripts/simple_pir_trigger.py --test

# Check if the photo was created
ls -l data/photos
```

## Run the PIR Sensor Test

```bash
# Start the PIR trigger script
./scripts/simple_pir_trigger.py
```

This will continuously monitor the PIR sensor and take a photo whenever motion is detected.

- The script uses GPIO pin 4 by default
- Photos will be saved to `~/backyard_bird_cam/data/photos/`
- Photos are taken at maximum resolution (4056×3040)
- State changes in the PIR sensor will be displayed for debugging

Press `Ctrl+C` to stop the program.

## Custom Settings

You can customize the script with these options:

```bash
# Change the GPIO pin (if your PIR is connected to a different pin)
./scripts/simple_pir_trigger.py --pin 17

# Change the cooldown time between photos (in seconds)
./scripts/simple_pir_trigger.py --cooldown 10

# Change the output directory
./scripts/simple_pir_trigger.py --output ~/my_bird_photos
```

## Run Automatically on Boot

To run the camera script automatically when the Pi boots:

```bash
# Edit the crontab
crontab -e

# Add this line (replace paths if necessary)
@reboot sleep 30 && cd /home/pi/backyard_bird_cam && python3 scripts/simple_pir_trigger.py >> /home/pi/backyard_bird_cam/camera.log 2>&1
```

The `sleep 30` gives the system time to fully boot before starting the camera script.

## Troubleshooting

1. **PIR sensor not triggering**
   - Check the wiring connections
   - Try a different GPIO pin
   - Adjust the sensitivity of the PIR sensor if it has hardware controls

2. **Camera not taking photos**
   - Ensure the camera is enabled in raspi-config
   - Check that the camera ribbon cable is properly connected
   - Run `vcgencmd get_camera` to verify the camera is detected

3. **"Failed to connect to pigpio daemon" error**
   - Run `sudo pigpiod` to start the daemon
   - If it persists, try `sudo killall pigpiod` then `sudo pigpiod`

4. **Permissions issues**
   - Ensure all scripts are executable: `chmod +x scripts/*.py scripts/*.sh`
   - Check that the data directory is writable: `chmod -R 755 data` 