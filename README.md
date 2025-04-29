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
git clone https://github.com/username/rpi_bird_camera_project.git
cd rpi_bird_camera_project
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

The system will:
1. Wait for motion to be detected by the PIR sensor
2. Capture a photo when motion is detected
3. Save the photo locally
4. (Optional) Upload the photo to cloud storage
5. (Optional) Run inference to detect and classify birds

## Project Structure

```
rpi_bird_camera_project/
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