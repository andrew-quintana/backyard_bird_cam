# Bird Camera System

A Raspberry Pi-based camera system for capturing photos of birds when motion is detected.

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi Zero 2 W)
- PIR motion sensor
- Camera module (compatible with libcamera/picamera2)
- Appropriate wiring and power supply

## Quick Start Installation

For a complete setup, run:

```
make setup
```

This will:
1. Install required dependencies
2. Configure environment variables
3. Set up the service file
4. Create necessary directories

After setup, you can install and start the service:

```
make install-service
```

## Manual Installation

If you prefer to install manually:

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
   cp config/env.example .env
   nano .env
   ```
   Edit the configuration values as needed for your setup.

## Usage

### System Status

Check the system status:
```
make status
```

### Running the Motion Detection System

Run manually:
```
make run
```

Or using Python directly:
```
python3 bird_cam.py
```

### Service Management

Install as a service:
```
make install-service
```

Remove the service:
```
make uninstall-service
```

### Checking Logs

- View service logs: `sudo journalctl -u bird_cam -n 50`
- View application logs: `cat motion_events.log`

## Configuration

The system can be configured through the `.env` file:

- `PIR_PIN`: GPIO pin for the PIR sensor (default: 4)
- `PHOTO_DIR`: Directory to store photos (default: "data/photos")
- `LOG_FILE`: Log file location (default: "motion_events.log")
- `COOLDOWN_TIME`: Time between motion triggers in seconds (default: 5)
- `CAMERA_ROTATION`: Rotation for the camera in degrees (default: 0)

## Project Structure

```
bird_cam/
├── bird_cam.py           # Main entry point script
├── config/               # Configuration files
│   └── env.example       # Example environment variables
├── data/                 # Data directory for photos
├── Makefile              # Common tasks
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── scripts/              # Helper scripts
│   ├── install.sh        # Installation script
│   ├── service/          # Service files
│   │   └── bird_cam.service
│   ├── setup/            # Setup scripts
│   │   └── setup.sh
│   └── status.sh         # Status checking script
├── setup.py              # Python package setup
├── src/                  # Source code
│   ├── camera/           # Camera handling
│   ├── config/           # Configuration
│   ├── inference/        # ML inference
│   ├── main.py           # Main module
│   ├── sensors/          # Sensor interfaces
│   ├── storage/          # Photo storage
│   └── uploader/         # Cloud uploading
└── tests/                # Tests
    ├── pytest.ini        # Test configuration
    └── test_*.py         # Test modules
```

## Development

Run tests:
```
make test
```

Install for development:
```
make install
```

## Troubleshooting

If you encounter issues:

1. Check system status: `make status`
2. Ensure GPIO access is enabled: `sudo raspi-config`
3. Check if the pigpio daemon is running: `systemctl status pigpiod`
4. Verify camera is working: `libcamera-still -o test.jpg`
5. Check permissions: Ensure user is in the `gpio` group
6. See TROUBLESHOOTING.md for more details 