# Raspberry Pi Bird Camera

A Raspberry Pi-based camera system designed to detect and photograph birds when motion is detected.

## Features

- Motion detection using PIR sensor
- Automatic photo capture with Raspberry Pi Camera
- Local storage for captured images
- Cloud upload capabilities (supporting S3, Dropbox, etc.)
- Bird detection and species classification using machine learning
- Configurable settings

## Hardware Requirements

- Raspberry Pi (3 or newer recommended)
- Raspberry Pi Camera Module
- PIR Motion Sensor
- Appropriate power supply
- (Optional) Housing/enclosure for outdoor use

## Software Requirements

- Python 3.7+
- Dependencies listed in requirements.txt

## Installation

1. Clone this repository:
```
git clone https://github.com/andrew-quintana/backyard_bird_cam.git
cd backyard_bird_cam
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure settings in `config.json` or use the default settings.

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

## Testing

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

# Test the settings module
python -m unittest tests/test_settings.py
```

### Testing on Hardware

The unit tests are designed to work both on development machines (using mocks) and on actual Raspberry Pi hardware (using real components).

When running on Raspberry Pi, you can verify each hardware component independently:

1. **Testing PIR Sensor**:
   ```bash
   # Run the PIR sensor tests (tests actual GPIO connections)
   python -m unittest tests/test_pir_sensor.py
   ```

2. **Testing Camera**:
   ```bash
   # Run the camera tests (tests Picamera2)
   python -m unittest tests/test_camera_handler.py
   ```

3. **Testing Storage**:
   ```bash
   # Run the storage tests
   python -m unittest tests/test_photo_storage.py
   ```

### Debugging Hardware Issues

For detailed debugging of hardware components, run the application with the `--debug` flag:
```bash
python src/main.py --debug
```

This will:
- Enable DEBUG level logging (more detailed than INFO)
- Log detailed information about hardware initialization and operations
- Output detailed logs to both console and the log file (`bird_camera.log`)

The debug logs can help identify issues with:
- PIR sensor connections and signal detection
- Camera initialization and photo capture
- Storage operations
- Configuration settings

## Project Structure

```
backyard_bird_cam/
├── src/
│   ├── camera/            # Camera handling
│   ├── config/            # Configuration settings
│   ├── inference/         # ML inference for bird detection
│   ├── sensors/           # PIR sensor interface
│   ├── storage/           # Local storage management
│   ├── uploader/          # Cloud upload functionality 
│   └── main.py            # Main application
├── tests/                 # Unit tests
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## Configuration

Edit `config.json` to customize settings:
- PIR sensor GPIO pin
- Camera resolution and rotation
- Storage directory and max photos
- Cloud service credentials
- ML model settings

## Development

### Running Tests

```
python -m unittest discover tests
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Run tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Troubleshooting

- Check PIR sensor connection if motion is not being detected
- Verify camera module is properly connected if photos aren't being captured
- Ensure proper permissions for storage directories
- Review logs in `bird_camera.log` for detailed error information
- Run with `--debug` flag for more detailed logs: `python src/main.py --debug` 