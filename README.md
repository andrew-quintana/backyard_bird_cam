# Raspberry Pi Bird Camera

A Raspberry Pi-based camera system designed to detect and photograph birds when motion is detected.

## Project Status

**Current Status: Development / Testing Phase**

- **PIR Sensor**: Working on calibration and troubleshooting (currently not detecting motion properly)
- **Camera Module**: Testing implementation (currently using mock camera fallback)
- **Storage System**: Functional, successfully storing photos with metadata
- **Service**: Systemd service created and functional for auto-start on boot

## Features

- Motion detection using PIR sensor
- Automatic photo capture with Raspberry Pi Camera
- Local storage for captured images
- Cloud upload capabilities (supporting S3, Dropbox, etc.)
- Bird detection and species classification using machine learning
- Configurable settings
- Systemd service for auto-start on boot

## Hardware Requirements

- Raspberry Pi (3 or newer recommended)
- Raspberry Pi Camera Module
- PIR Motion Sensor
- Appropriate power supply
- (Optional) Housing/enclosure for outdoor use

## Software Requirements

- Python 3.7+
- Picamera2 library
- RPi.GPIO library
- Other dependencies listed in requirements.txt

## Installation

1. Clone this repository:
```
git clone https://github.com/andrew-quintana/backyard_bird_cam.git
cd backyard_bird_cam
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Configure settings in `config.json` or use the default settings.

5. Set up as a service (optional):
```
sudo cp systemd/bird_camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bird_camera.service
sudo systemctl start bird_camera.service
```

## Usage

Run the main application:
```
python src/main.py
```

To run with detailed debug logging enabled:
```
python src/main.py --debug
```

The system will:
1. Wait for motion to be detected by the PIR sensor
2. Capture a photo when motion is detected
3. Save the photo locally
4. (Optional) Upload the photo to cloud storage
5. (Optional) Run inference to detect and classify birds

## Testing and Calibration

### Hardware Testing Tools

The project includes dedicated tools for testing and calibrating hardware components:

- **PIR sensor tests**: Located in `tools/hardware_tests/`
  ```
  python tools/hardware_tests/check_pir_directly.py --pin 17
  python tools/hardware_tests/check_inverted_pir.py --pin 17 --pullup
  python tools/hardware_tests/long_pir_warmup.py --pin 17 --warmup 120
  ```

- **Calibration tools**: Located in `tools/calibration/`
  ```
  python tools/calibration/calibrate_pir.py --csv > pir_data.csv
  python tools/calibration/analyze_pir_data.py pir_data.csv
  ```

### Running Unit Tests

Run all tests:
```bash
# Run all tests
python -m unittest discover tests
```

Run tests for specific components:
```bash
# Test the PIR sensor
python -m unittest tests/test_pir_sensor.py

# Test the camera
python -m unittest tests/test_camera_handler.py

# Test the photo storage
python -m unittest tests/test_photo_storage.py
```

## Project Structure

```
backyard_bird_cam/
├── src/                  # Main source code
│   ├── camera/           # Camera handling
│   ├── config/           # Configuration settings
│   ├── inference/        # ML inference for bird detection
│   ├── sensors/          # PIR sensor interface
│   ├── storage/          # Local storage management
│   ├── uploader/         # Cloud upload functionality 
│   └── main.py           # Main application
├── tests/                # Unit tests
├── tools/                # Utility tools
│   ├── calibration/      # Tools for calibrating sensors
│   └── hardware_tests/   # Tools for testing hardware components
├── systemd/              # Systemd service files
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

## Configuration

Edit `config.json` to customize settings:
- PIR sensor GPIO pin and trigger cooldown
- Camera resolution and rotation
- Storage directory and max photos
- Cloud service credentials
- ML model settings

## Troubleshooting

### PIR Sensor Issues
- Check wiring connections
- Try different GPIO pins
- Test with both pull-up and pull-down resistor configurations
- Ensure sensor has sufficient warm-up time (2-3 minutes)
- Use the hardware test tools in `tools/hardware_tests/`

### Camera Issues
- Verify Picamera2 library is properly installed
- Check camera is properly connected to the Raspberry Pi
- Make sure camera is enabled in Raspberry Pi configuration
- Check camera isn't in mock mode due to missing dependencies

### Storage Issues
- Ensure proper permissions for storage directories
- Verify sufficient disk space

### Service Issues
- Check service status: `sudo systemctl status bird_camera.service`
- View logs: `sudo journalctl -u bird_camera.service -f`

## License

MIT License - See LICENSE file for details 