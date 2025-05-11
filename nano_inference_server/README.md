# Jetson Nano Bird Detection Inference Server

A modular inference server for the Jetson Nano that:
1. Monitors directories for new bird images
2. Runs detection and classification models
3. Stores and serves results through a web interface
4. Provides a REST API for integration

## Features

- **Automatic Monitoring**: Watches for new images uploaded from Raspberry Pi cameras
- **Powerful Inference**: Uses TensorRT/CUDA-accelerated models for fast bird detection
- **Beautiful Web Gallery**: Browse, filter, and view detection results
- **Modern V0.dev UI**: Optional modern React UI built with V0.dev components
- **REST API**: Programmatically access results for integration with other systems
- **Secure Access**: Optional API key authentication and rate limiting
- **Remote Access**: Integrated Cloudflare Tunnel support for secure HTTPS access
- **Modular Design**: Easily extensible for custom models and integrations

## Quick Start

### Prerequisites

- Jetson Nano with JetPack 4.6+
- Python 3.6+
- Camera module sending images to the monitored directory
- Node.js and npm (for V0.dev UI only)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourname/backyard_bird_cam.git
   cd backyard_bird_cam/nano_inference_server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the server:
   ```bash
   # Edit the config.json file with your settings
   nano config.json
   ```

4. Run the server:
   ```bash
   python main.py
   ```

5. Access the web interface at `http://localhost:5000`

## Configuration

The server is configured through `config.json`:

```json
{
    "model_path": "models/bird_model.pb",
    "model_type": "mobilenet",
    "confidence_threshold": 0.5,
    "device": "cuda",
    
    "input_dir": "data/input",
    "output_dir": "data/output",
    "max_results": 10000,
    "organize_by_date": true,
    
    "file_patterns": [".*\\.(jpg|jpeg|png)$"],
    
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "access_key": null,
    "rate_limit": 100,
    
    "use_v0_ui": true,
    "v0_ui_primary": false,
    
    "cloudflared": {
        "enabled": false,
        "tunnel_token": null
    }
}
```

## Web Interfaces

The inference server provides two web interface options:

### 1. Standard Bootstrap UI

This is the default UI, accessible at `http://localhost:5000/` when `v0_ui_primary` is set to `false`.

- Simple, lightweight design
- Works without JavaScript
- No additional dependencies

### 2. Modern V0.dev UI

A React-based modern UI, accessible at `http://localhost:5000/v0` or as the primary UI when `v0_ui_primary` is set to `true`.

- Modern, responsive design with advanced features
- Rich interactive components
- Requires building before use

#### Building the V0.dev UI

To use the V0.dev UI, you need to build it first:

```bash
# Navigate to the v0_ui directory
cd api/v0_ui

# Install dependencies and build the UI
./build_for_flask.sh

# Or to set it as the primary interface
./build_for_flask.sh --primary
```

You need Node.js and npm installed to build the V0.dev UI.

## Command-Line Arguments

```
usage: main.py [-h] [--config CONFIG] [--model MODEL] [--input-dir INPUT_DIR]
               [--output-dir OUTPUT_DIR] [--model-type {mobilenet,yolo}]
               [--port PORT] [--debug] [--process-existing] [--no-server]

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to configuration file
  --model MODEL, -m MODEL
                        Path to model file
  --input-dir INPUT_DIR, -i INPUT_DIR
                        Directory to monitor for new images
  --output-dir OUTPUT_DIR, -o OUTPUT_DIR
                        Directory to store results
  --model-type {mobilenet,yolo}, -t {mobilenet,yolo}
                        Type of model to use
  --port PORT, -p PORT  Port for the web server
  --debug, -d           Enable debug logging
  --process-existing, -e
                        Process existing files in the input directory
  --no-server           Don't start the web server
```

## Remote Access with Cloudflare Tunnel

For secure access from anywhere:

1. Install cloudflared:
   ```bash
   python cloudflared_setup.py --download
   ```

2. Create a tunnel in the Cloudflare Zero Trust dashboard

3. Update your config.json with the tunnel token:
   ```json
   "cloudflared": {
       "enabled": true,
       "tunnel_token": "your-tunnel-token"
   }
   ```

4. Generate and start the tunnel:
   ```bash
   python cloudflared_setup.py --start
   ```

## API Documentation

The REST API provides the following endpoints:

- `GET /api/results` - List detection results
- `GET /api/results/<id>` - Get a specific detection
- `GET /api/search` - Search for detections
- `GET /api/stats` - Get detection statistics
- `POST /api/upload` - Upload a new image for processing

## Project Structure

```
nano_inference_server/
├── api/               # Web API and interface
│   ├── server.py      # Flask server implementation
│   └── templates/     # HTML templates
├── inference/         # ML model handling
│   └── model.py       # Model loading and inference
├── monitoring/        # Directory monitoring
│   └── directory_monitor.py  # File system watcher
├── storage/           # Result storage
│   └── result_storage.py     # SQLite storage for results
├── config.json        # Server configuration
├── main.py            # Main entry point
├── cloudflared_setup.py  # Cloudflare Tunnel setup
└── requirements.txt   # Python dependencies
```

## Troubleshooting

If you encounter issues:

1. Check the logs for error messages
2. Verify your model file exists and is compatible
3. Ensure the input directory is accessible and monitored
4. Confirm network connectivity if using remote access
5. Make sure the Jetson has sufficient resources (RAM/storage)

## License

MIT 