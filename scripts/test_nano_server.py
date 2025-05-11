#!/usr/bin/env python3
"""
Simple test server for the Jetson Nano to respond to connectivity tests from the Pi.
Run this on the Nano while setting up to verify connectivity.

Usage:
  python3 test_nano_server.py [--port PORT]
  Default port is 8000 if not specified.
"""

import argparse
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import sys

def get_ip_address():
    """Get the primary IP address of this machine"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class TestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self._set_headers()
            response = {
                "status": "ok",
                "timestamp": time.time(),
                "message": "Jetson Nano test server is running"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            self._set_headers("text/html")
            self.wfile.write(b"<html><body><h1>Jetson Nano Test Server</h1><p>Server is running.</p></body></html>")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/test":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                print(f"Received test message: {data}")
                
                self._set_headers()
                response = {
                    "status": "received",
                    "timestamp": time.time(),
                    "message": "Test message received successfully",
                    "received_data": data
                }
                self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to provide better logging"""
        sys.stdout.write("%s - %s\n" % (self.client_address[0], format % args))

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHandler)
    ip = get_ip_address()
    
    print(f"Starting test server on {ip}:{port}")
    print(f"To test connectivity from the Pi, run:")
    print(f"python3 test_pi_nano_connectivity.py {ip} --port {port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        httpd.server_close()

def main():
    parser = argparse.ArgumentParser(description='Run a test server on the Jetson Nano')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on (default: 8000)')
    
    args = parser.parse_args()
    run_server(args.port)

if __name__ == "__main__":
    main() 