#!/bin/bash
# Simple installation script for the Nano Inference Server

echo "Installing Nano Inference Server..."

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated."
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Install package in development mode
echo "Installing package..."
pip3 install -e .

echo "Installation complete!"
echo "To start the server, run: python main.py"
echo "For deployment options, see: ../deploy/jetson/deploy_inference_server.sh" 