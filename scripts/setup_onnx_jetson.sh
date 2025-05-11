#!/bin/bash

echo "Setting up dependencies for ONNX inference on Jetson Nano"

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install Python development packages and other dependencies
echo "Installing Python development packages and dependencies..."
sudo apt-get install -y python3-pip python3-dev libopenblas-dev libopenmpi-dev

# Install numpy and OpenCV
echo "Installing numpy and OpenCV..."
pip3 install numpy opencv-python

# Install ONNX Runtime
echo "Installing ONNX Runtime..."
pip3 install onnxruntime

# Alternative: If the above doesn't work, try this for Jetson Nano
# (ONNX Runtime has specific wheels for Jetson)
# pip3 install --extra-index-url https://jetson-wheel-index.co/onnxruntime-jetson

echo "Setup complete! You can now run the test script:"
echo "python3 scripts/test_onnx_model.py" 