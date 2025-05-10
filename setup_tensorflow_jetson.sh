#!/bin/bash
# TensorFlow installation script for Jetson Nano
# This installs the NVIDIA-optimized version of TensorFlow for Jetson

set -e  # Exit on error

echo "===== Jetson Nano TensorFlow Installation ====="
echo "This script will install TensorFlow optimized for Jetson Nano"
echo

# Check if running on Jetson 
if [ "$(uname -m)" != "aarch64" ]; then
    echo "WARNING: This script is intended for Jetson Nano (aarch64 architecture)"
    echo "Current architecture: $(uname -m)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran

echo "Installing Python dependencies..."
pip3 install --user -U pip testresources setuptools numpy==1.19.5 future==0.18.2 mock==3.0.5 keras_preprocessing==1.1.2 keras_applications==1.0.8 gast==0.4.0 protobuf==3.9.2 cython pkgconfig

# Install specific TensorFlow version for Jetson
echo "Installing TensorFlow for Jetson..."
pip3 install --user --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v46 tensorflow==2.5.0+nv21.8

# Test TensorFlow installation
echo
echo "Testing TensorFlow installation..."
python3 -c "import tensorflow as tf; print('TensorFlow version:', tf.__version__); print('Num GPUs Available: ', len(tf.config.experimental.list_physical_devices('GPU')))"

echo
echo "===== TensorFlow Installation Complete ====="
echo "Please restart your terminal session for changes to take effect." 