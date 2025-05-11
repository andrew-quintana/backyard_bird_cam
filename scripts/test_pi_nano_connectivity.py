#!/usr/bin/env python3
"""
Simple test script to verify connectivity between Raspberry Pi and Jetson Nano.
This can be run on the Pi to test if it can communicate with the Nano.

Usage:
  On Pi: python3 test_pi_nano_connectivity.py <nano_ip_address> [port]
  Default port is 8000 if not specified.
"""

import sys
import socket
import time
import requests
import argparse
import json

def check_basic_connectivity(host, port=22):
    """Test basic connectivity to the host using a socket connection."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((host, port))
        s.close()
        print(f"✅ Basic connectivity to {host}:{port} successful")
        return True
    except socket.error as e:
        print(f"❌ Cannot connect to {host}:{port}: {e}")
        return False

def check_http_connectivity(host, port=8000):
    """Test HTTP connectivity to the host."""
    url = f"http://{host}:{port}/health"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ HTTP connectivity to {host}:{port} successful")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ HTTP request failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP connection failed: {e}")
        # Try a simpler endpoint in case /health isn't implemented
        try:
            alt_url = f"http://{host}:{port}/"
            response = requests.get(alt_url, timeout=10)
            print(f"✅ Basic HTTP connectivity to {host}:{port} successful")
            return True
        except:
            return False

def send_test_message(host, port=8000):
    """Send a test message to the server."""
    url = f"http://{host}:{port}/test"
    payload = {"test": "message", "timestamp": time.time()}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Test message sent successfully to {host}:{port}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ Test message failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send test message: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test connectivity to Jetson Nano')
    parser.add_argument('host', help='IP address or hostname of the Jetson Nano')
    parser.add_argument('--port', type=int, default=8000, help='Port for HTTP tests (default: 8000)')
    parser.add_argument('--ssh', action='store_true', help='Also test SSH connectivity')
    
    args = parser.parse_args()
    
    print(f"Testing connectivity to Jetson Nano at {args.host}...")
    
    # Test basic connectivity
    basic_conn = check_basic_connectivity(args.host, args.port)
    
    # Test SSH if requested
    if args.ssh:
        ssh_conn = check_basic_connectivity(args.host, 22)
        if not ssh_conn:
            print("SSH connectivity failed - make sure SSH is enabled on the Nano")
    
    # Test HTTP connectivity
    http_conn = check_http_connectivity(args.host, args.port)
    
    # Send test message if HTTP connectivity works
    if http_conn:
        send_test_message(args.host, args.port)
    
    # Print summary
    print("\n-------- Connectivity Test Summary --------")
    print(f"{'✅' if basic_conn else '❌'} Basic TCP connectivity to {args.host}:{args.port}")
    if args.ssh:
        print(f"{'✅' if ssh_conn else '❌'} SSH connectivity")
    print(f"{'✅' if http_conn else '❌'} HTTP connectivity")
    
    if basic_conn:
        print("\nTCP connection is working - the Nano is reachable on the network.")
        if not http_conn:
            print("HTTP connection failed - the inference server might not be running yet.")
            print("You may need to wait for the setup to complete or check the server logs.")
    else:
        print("\nCouldn't establish a connection to the Nano.")
        print("Please check:")
        print("1. Both devices are on the same network")
        print("2. IP address is correct")
        print("3. No firewall is blocking the connection")
        print("4. The Nano is powered on and booted up")

if __name__ == "__main__":
    main() 