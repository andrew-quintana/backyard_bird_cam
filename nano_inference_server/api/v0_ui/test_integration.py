#!/usr/bin/env python3
"""
Quick test script to verify that the V0.dev UI and Flask integration works.
This script:
1. Checks if the V0.dev UI build exists
2. Optionally starts a temporary Flask server
3. Makes test requests to verify the API endpoints
"""
import os
import sys
import time
import argparse
import subprocess
import webbrowser
import platform
import requests

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from storage.result_storage import ResultStorage
from inference.model import ModelHandler

# Default paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(CURRENT_DIR, 'out')
API_SERVER_PATH = os.path.join(os.path.dirname(CURRENT_DIR), 'server.py')

def check_build_exists():
    """Check if the V0.dev UI build exists"""
    if not os.path.exists(OUT_DIR):
        print("ERROR: V0.dev UI build not found. Please run the build script first:")
        print("  cd nano_inference_server/api/v0_ui && ./build_for_flask.sh")
        return False
    
    # Check if index.html exists
    if not os.path.exists(os.path.join(OUT_DIR, 'index.html')):
        print("ERROR: index.html not found in the build directory.")
        return False
    
    print("✓ V0.dev UI build found.")
    return True

def check_api_endpoints(base_url="http://localhost:5000"):
    """Test API endpoints"""
    print("Testing API endpoints...")
    endpoints = [
        "/api/stats",
        "/api/results?limit=1",
    ]
    
    success = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✓ {endpoint} - OK ({response.status_code})")
            else:
                print(f"✗ {endpoint} - Failed ({response.status_code})")
                success = False
        except Exception as e:
            print(f"✗ {endpoint} - Error: {str(e)}")
            success = False
    
    return success

def start_test_server(port=5000):
    """Start a temporary Flask server for testing"""
    print("Starting a temporary Flask server...")
    
    # Create a simple storage with mock data
    data_dir = os.path.join(CURRENT_DIR, 'test_data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize a simple storage and model
    storage = ResultStorage(base_dir=data_dir)
    model = None
    try:
        model = ModelHandler(model_path="models/bird_model.pb")
    except Exception as e:
        print(f"Warning: Could not load model: {str(e)}")
    
    # Import the API server here to avoid circular imports
    sys.path.insert(0, os.path.dirname(API_SERVER_PATH))
    from server import APIServer
    
    # Create and run the server
    config = {
        "port": port,
        "debug": True,
        "use_v0_ui": True,
        "v0_ui_primary": False
    }
    
    server = APIServer(storage=storage, model=model, config=config)
    
    print(f"Server running at http://localhost:{port}/v0")
    print("Press Ctrl+C to stop the server.")
    
    # Open the browser
    if platform.system() != "Linux":  # Don't open browser on headless systems
        webbrowser.open(f"http://localhost:{port}/v0")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("Server stopped.")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test V0.dev UI integration")
    parser.add_argument("--port", type=int, default=5000, help="Port for the test server")
    parser.add_argument("--run-server", action="store_true", help="Start a test server")
    parser.add_argument("--check-api", action="store_true", help="Check API endpoints")
    
    args = parser.parse_args()
    
    # Check if the build exists
    if not check_build_exists():
        return 1
    
    # Check API endpoints if requested
    if args.check_api:
        if not check_api_endpoints(f"http://localhost:{args.port}"):
            return 1
    
    # Start a test server if requested
    if args.run_server:
        start_test_server(args.port)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 