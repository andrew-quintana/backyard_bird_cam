# Bird Camera System

A Raspberry Pi-based camera system for capturing photos of birds when motion is detected.

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi Zero 2 W)
- PIR motion sensor
- Camera module (compatible with libcamera/picamera2)
- Appropriate wiring and power supply

## Installation

1. Clone this repository to your Raspberry Pi:
   ```
   git clone https://github.com/USERNAME/bird_cam.git
   cd bird_cam
   ```

2. Install dependencies:
   ```
   sudo apt update
   sudo apt install -y python3-pip python3-picamera2 python3-pigpio libcamera-dev
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   pip3 install -r requirements.txt
   ```

3. Setup the hardware:
   - Connect the PIR sensor to GPIO pin 4 (BCM numbering)
   - Connect the camera module to the CSI port

4. Configure environment variables:
   ```
   cp env.example .env
   nano .env
   ```
   Edit the configuration values as needed for your setup.

## Usage

### Testing the Components

- Test the camera: `python3 tests/test_camera.py`
- Test the PIR sensor: `python3 tests/test_pir.py`

### Running the Motion Detection System

Run manually:
```
python3 pir_motion_detector.py
```

Run as a service:
```
sudo cp bird_cam.service /etc/systemd/system/
sudo systemctl enable bird_cam
sudo systemctl start bird_cam
```

### Checking Logs

- View service logs: `sudo journalctl -u bird_cam`
- View application logs: `cat motion_events.log`

## Configuration

The system can be configured through the `.env` file:

- `PIR_PIN`: GPIO pin for the PIR sensor (default: 4)
- `PHOTO_DIR`: Directory to store photos (default: "data/photos")
- `LOG_FILE`: Log file location (default: "motion_events.log")
- `COOLDOWN_TIME`: Time between motion triggers in seconds (default: 5)
- `CAMERA_ROTATION`: Rotation for the camera in degrees (default: 0)

## Troubleshooting

If you encounter issues:

1. Ensure GPIO access is enabled: `sudo raspi-config`
2. Check if the pigpio daemon is running: `systemctl status pigpiod`
3. Verify camera is working: `libcamera-still -o test.jpg`
4. Check permissions: Ensure user is in the `gpio` group
5. Check the .env file is properly configured 