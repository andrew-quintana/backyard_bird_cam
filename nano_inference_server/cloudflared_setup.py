#!/usr/bin/env python3
"""
Setup script for Cloudflare Tunnel integration.
Allows the inference server to be securely accessible from the internet.
"""
import os
import sys
import json
import logging
import argparse
import subprocess
import time
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_cloudflared_installed():
    """Check if cloudflared is installed and get its version"""
    try:
        result = subprocess.run(["cloudflared", "--version"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split(" ")[2]
            logger.info(f"cloudflared is installed (version {version})")
            return True, version
        return False, None
    except FileNotFoundError:
        logger.info("cloudflared is not installed")
        return False, None


def download_cloudflared():
    """Download cloudflared binary for the current platform"""
    try:
        # Determine platform-specific download URL
        import platform
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "linux":
            if machine == "x86_64" or machine == "amd64":
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
            elif "arm" in machine:
                if "64" in machine:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
                else:
                    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
            else:
                logger.error(f"Unsupported Linux architecture: {machine}")
                return False
        elif system == "darwin":  # macOS
            if "arm64" in machine:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
            else:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
        elif system == "windows":
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        else:
            logger.error(f"Unsupported platform: {system}")
            return False
        
        # Create bin directory if it doesn't exist
        bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
        os.makedirs(bin_dir, exist_ok=True)
        
        # Download the binary
        cloudflared_path = os.path.join(bin_dir, "cloudflared" + (".exe" if system == "windows" else ""))
        logger.info(f"Downloading cloudflared from {url}...")
        
        result = subprocess.run(["curl", "-L", "--output", cloudflared_path, url],
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Failed to download cloudflared: {result.stderr}")
            return False
        
        # Make the binary executable (except on Windows)
        if system != "windows":
            os.chmod(cloudflared_path, 0o755)
        
        logger.info(f"cloudflared downloaded to {cloudflared_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error downloading cloudflared: {e}")
        return False


def generate_tunnel_config(config, force=False):
    """Generate configuration for Cloudflare Tunnel"""
    try:
        tunnel_config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared")
        os.makedirs(tunnel_config_dir, exist_ok=True)
        
        config_path = os.path.join(tunnel_config_dir, "config.yml")
        
        # Skip if config file already exists and force is False
        if os.path.exists(config_path) and not force:
            logger.info(f"Tunnel config already exists at {config_path}")
            return True
        
        # Get values from the config
        port = config.get("port", 5000)
        host = config.get("host", "0.0.0.0")
        
        # If host is 0.0.0.0, set to localhost for tunneling
        if host == "0.0.0.0":
            host = "localhost"
        
        # Create config.yml content
        config_content = f"""
# Cloudflare Tunnel configuration for Bird Detection Server
tunnel: {config['cloudflared'].get('tunnel_token', 'YOUR_TUNNEL_TOKEN_HERE')}
credentials-file: {os.path.join(tunnel_config_dir, 'credentials.json')}

# Disable TLS verification when connecting to local services
no-tls-verify: true

# Ingress rules defining how to route incoming requests
ingress:
  # Route all traffic to the bird detection server
  - service: http://{host}:{port}
  
  # Catch-all rule to return 404 for anything else
  - service: http_status:404
"""
        
        # Write the config file
        with open(config_path, 'w') as f:
            f.write(config_content)
            
        logger.info(f"Tunnel configuration generated at {config_path}")
        
        # Explain next steps if no token provided
        if config['cloudflared'].get('tunnel_token') is None:
            logger.info("\nNOTE: You need to set up a Cloudflare Tunnel and update the configuration:")
            logger.info("1. Log in to the Cloudflare Zero Trust dashboard")
            logger.info("2. Go to Access > Tunnels and create a new tunnel")
            logger.info("3. Copy the tunnel token/ID")
            logger.info("4. Update your config.json with the token")
            logger.info("5. Re-run this script with --force to update the configuration")
        
        return True
    
    except Exception as e:
        logger.error(f"Error generating tunnel config: {e}")
        return False


def start_tunnel(config_dir=None):
    """Start the Cloudflare Tunnel"""
    try:
        # Determine the config directory
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared")
        
        config_path = os.path.join(config_dir, "config.yml")
        
        if not os.path.exists(config_path):
            logger.error(f"Tunnel configuration not found at {config_path}")
            return False
        
        # Find cloudflared binary
        cloudflared_path = shutil.which("cloudflared")
        if cloudflared_path is None:
            # Try local binary
            local_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "cloudflared")
            if os.path.exists(local_bin):
                cloudflared_path = local_bin
            else:
                logger.error("cloudflared binary not found. Please install it or download it first.")
                return False
        
        # Start the tunnel
        logger.info(f"Starting Cloudflare Tunnel with config from {config_path}")
        
        # Command to run the tunnel as a subprocess
        cmd = [cloudflared_path, "tunnel", "--config", config_path, "run"]
        
        # Run in a new process that will continue after this script exits
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit to see if it starts successfully
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is None:
            logger.info("Cloudflare Tunnel started successfully")
            
            # Try to read the URL from the output
            for _ in range(5):  # Try a few times
                output = process.stdout.readline()
                if "connector" in output and "https://" in output:
                    url = output.split("https://")[1].split()[0]
                    logger.info(f"Your site is available at: https://{url}")
                    break
                time.sleep(0.5)
            
            logger.info("The tunnel will continue running in the background")
            return True
        else:
            # If the process exited, get the error message
            stderr = process.stderr.read()
            logger.error(f"Tunnel failed to start: {stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Error starting tunnel: {e}")
        return False


def main():
    """Main function to setup and configure Cloudflare Tunnel"""
    parser = argparse.ArgumentParser(description="Setup Cloudflare Tunnel for Bird Detection Server")
    
    parser.add_argument("--config", "-c", default="../config.json", 
                       help="Path to the server configuration file")
    parser.add_argument("--download", "-d", action="store_true",
                       help="Download cloudflared binary")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force regeneration of configuration files")
    parser.add_argument("--start", "-s", action="store_true",
                       help="Start the tunnel after setup")
    
    args = parser.parse_args()
    
    try:
        # Load the server configuration
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Check if cloudflared is already installed
        installed, version = check_cloudflared_installed()
        
        # Download if requested or not installed
        if args.download or not installed:
            if download_cloudflared():
                logger.info("cloudflared downloaded successfully")
            else:
                logger.error("Failed to download cloudflared")
                return 1
        
        # Generate tunnel configuration
        if generate_tunnel_config(config, args.force):
            logger.info("Tunnel configuration generated successfully")
        else:
            logger.error("Failed to generate tunnel configuration")
            return 1
        
        # Start the tunnel if requested
        if args.start:
            if config['cloudflared'].get('tunnel_token') is None:
                logger.error("Cannot start tunnel: No tunnel token provided in config")
                logger.info("Please update your config.json with a valid tunnel token first")
                return 1
            
            if start_tunnel():
                logger.info("Tunnel started successfully")
            else:
                logger.error("Failed to start tunnel")
                return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 