#!/bin/bash
# Build script for integrating V0.dev UI with the Flask server

# Set error handling
set -e

echo "Building V0.dev UI for Flask integration..."

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install Node.js and npm first."
    exit 1
fi

# Set environment variables for base path
if [ -z "$1" ]; then
    # Default to /v0 path if no argument provided
    export NEXT_PUBLIC_BASE_PATH="/v0"
else
    # Use provided base path
    export NEXT_PUBLIC_BASE_PATH="$1"
fi

echo "Using base path: $NEXT_PUBLIC_BASE_PATH"

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the Next.js application
echo "Building the application..."
npm run build

# Check if build was successful
if [ ! -d "out" ]; then
    echo "Error: Build failed. The 'out' directory wasn't created."
    exit 1
fi

echo "Build completed successfully!"
echo "The static files are in the 'out' directory."
echo ""
echo "To use the V0.dev UI with the Flask server:"
echo "1. Make sure 'use_v0_ui' is set to true in nano_inference_server/config.json"
echo "2. Start the server with 'python main.py'"
echo "3. Access the UI at http://localhost:5000/v0"
echo ""

# Check if we should set as primary interface
if [ "$2" == "--primary" ]; then
    echo "Setting V0.dev UI as the primary interface..."
    echo "To make this permanent, set 'v0_ui_primary' to true in nano_inference_server/config.json"
fi

exit 0 