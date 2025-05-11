#!/bin/bash
#
# Deployment script for the Nano Inference Server
# Sets up and configures the bird detection inference server on the Jetson Nano.
#

# Exit on error
set -e

# Set default constants
REPO_DIR="$HOME/backyard_bird_cam"
INFERENCE_DIR="$REPO_DIR/nano_inference_server"
DATA_DIR="$HOME/bird_data"
MODEL_DIR="$DATA_DIR/models"
INPUT_DIR="$DATA_DIR/input"
OUTPUT_DIR="$DATA_DIR/output"
CONFIG_FILE="$INFERENCE_DIR/config.json"
SERVICE_FILE="/etc/systemd/system/bird-inference.service"
CLOUDFLARED_ENABLED=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}====================================${NC}"
echo -e "${GREEN}   Bird Detection Inference Server  ${NC}"
echo -e "${GREEN}   Deployment Script for Jetson Nano${NC}"
echo -e "${GREEN}====================================${NC}"
echo ""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --repo-dir)
      REPO_DIR="$2"
      shift 2
      ;;
    --data-dir)
      DATA_DIR="$2"
      shift 2
      ;;
    --model-path)
      MODEL_PATH="$2"
      shift 2
      ;;
    --model-type)
      MODEL_TYPE="$2"
      shift 2
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --cloudflared)
      CLOUDFLARED_ENABLED=true
      shift
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --repo-dir DIR       Repository directory (default: $REPO_DIR)"
      echo "  --data-dir DIR       Data directory (default: $DATA_DIR)"
      echo "  --model-path PATH    Path to model file"
      echo "  --model-type TYPE    Model type (mobilenet or yolo)"
      echo "  --port PORT          Web server port (default: 5000)"
      echo "  --cloudflared        Enable Cloudflare Tunnel setup"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if running on Jetson Nano
check_jetson() {
  if [ -f /etc/nv_tegra_release ]; then
    echo -e "${GREEN}✓ Running on Jetson device${NC}"
    return 0
  else
    echo -e "${YELLOW}⚠ Not running on a Jetson device. Some features may not work correctly.${NC}"
    return 1
  fi
}

# Set up directory structure
setup_directories() {
  echo -e "\n${GREEN}Setting up directory structure...${NC}"
  
  mkdir -p "$DATA_DIR"
  mkdir -p "$MODEL_DIR"
  mkdir -p "$INPUT_DIR"
  mkdir -p "$OUTPUT_DIR"
  
  echo -e "${GREEN}✓ Directories created${NC}"
}

# Install dependencies
install_dependencies() {
  echo -e "\n${GREEN}Installing dependencies...${NC}"
  
  if ! command_exists pip3; then
    echo -e "${YELLOW}Installing pip3...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3-pip
  fi
  
  cd "$INFERENCE_DIR"
  
  echo -e "${YELLOW}Installing Python packages...${NC}"
  pip3 install -r requirements.txt
  
  echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Configure the server
configure_server() {
  echo -e "\n${GREEN}Configuring the server...${NC}"
  
  # Create or update config file
  if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}Existing config file found. Creating backup...${NC}"
    cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
  fi
  
  # Set default values
  if [ -z "$MODEL_PATH" ]; then
    MODEL_PATH="$MODEL_DIR/bird_model.pb"
  fi
  
  if [ -z "$MODEL_TYPE" ]; then
    MODEL_TYPE="mobilenet"
  fi
  
  if [ -z "$PORT" ]; then
    PORT=5000
  fi
  
  # Create the config file
  cat > "$CONFIG_FILE" <<EOL
{
    "model_path": "$MODEL_PATH",
    "model_type": "$MODEL_TYPE",
    "confidence_threshold": 0.5,
    "device": "cuda",
    
    "input_dir": "$INPUT_DIR",
    "output_dir": "$OUTPUT_DIR",
    "max_results": 10000,
    "organize_by_date": true,
    
    "file_patterns": [".*\\\\.(jpg|jpeg|png)$"],
    
    "host": "0.0.0.0",
    "port": $PORT,
    "debug": false,
    "access_key": null,
    "rate_limit": 100,
    
    "cloudflared": {
        "enabled": $CLOUDFLARED_ENABLED,
        "tunnel_token": null
    }
}
EOL
  
  echo -e "${GREEN}✓ Configuration file created: $CONFIG_FILE${NC}"
}

# Set up systemd service
setup_service() {
  echo -e "\n${GREEN}Setting up systemd service...${NC}"
  
  # Create service file
  cat > /tmp/bird-inference.service <<EOL
[Unit]
Description=Bird Detection Inference Server
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$INFERENCE_DIR
ExecStart=/usr/bin/python3 $INFERENCE_DIR/main.py --config $CONFIG_FILE
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL
  
  sudo mv /tmp/bird-inference.service $SERVICE_FILE
  sudo systemctl daemon-reload
  
  echo -e "${GREEN}✓ Service file created: $SERVICE_FILE${NC}"
  
  # Enable and start the service
  echo -e "${YELLOW}Do you want to enable and start the service now? (y/n) ${NC}"
  read -r response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo systemctl enable bird-inference.service
    sudo systemctl start bird-inference.service
    echo -e "${GREEN}✓ Service enabled and started${NC}"
  else
    echo -e "${YELLOW}Service not started. You can start it manually with:${NC}"
    echo -e "  sudo systemctl start bird-inference.service"
  fi
}

# Set up Cloudflare Tunnel
setup_cloudflare() {
  if [ "$CLOUDFLARED_ENABLED" = true ]; then
    echo -e "\n${GREEN}Setting up Cloudflare Tunnel...${NC}"
    
    cd "$INFERENCE_DIR"
    
    # Download cloudflared binary
    python3 cloudflared_setup.py --download
    
    # Generate the config file
    python3 cloudflared_setup.py --config "$CONFIG_FILE"
    
    echo -e "${GREEN}✓ Cloudflare Tunnel setup completed${NC}"
    echo -e "${YELLOW}⚠ NOTE: You need to update config.json with your tunnel token${NC}"
    echo -e "${YELLOW}   Then run: python3 $INFERENCE_DIR/cloudflared_setup.py --start${NC}"
  fi
}

# Test the server
test_server() {
  echo -e "\n${GREEN}Testing the server...${NC}"
  
  # Check if the server is running
  if systemctl is-active --quiet bird-inference.service; then
    echo -e "${GREEN}✓ Server is running${NC}"
    
    # Test the API
    if command_exists curl; then
      echo -e "${YELLOW}Testing API...${NC}"
      if curl -s "http://localhost:$PORT/api/stats" | grep -q "total_detections"; then
        echo -e "${GREEN}✓ API test successful${NC}"
      else
        echo -e "${RED}✗ API test failed${NC}"
      fi
    fi
  else
    echo -e "${YELLOW}Server is not running. Start it with:${NC}"
    echo -e "  sudo systemctl start bird-inference.service"
    
    # Try running manually for testing
    echo -e "${YELLOW}Do you want to test the server manually? (y/n) ${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
      cd "$INFERENCE_DIR"
      python3 main.py --config "$CONFIG_FILE" &
      server_pid=$!
      
      echo -e "${YELLOW}Server started with PID $server_pid. Press Enter to stop...${NC}"
      read -r
      
      kill $server_pid
      echo -e "${GREEN}✓ Test completed${NC}"
    fi
  fi
}

# Show summary
show_summary() {
  echo -e "\n${GREEN}====================================${NC}"
  echo -e "${GREEN}   Deployment Summary              ${NC}"
  echo -e "${GREEN}====================================${NC}"
  echo -e "Repository Dir: $REPO_DIR"
  echo -e "Data Dir:       $DATA_DIR"
  echo -e "Config File:    $CONFIG_FILE"
  echo -e "Service File:   $SERVICE_FILE"
  echo -e "Web Interface:  http://localhost:$PORT"
  echo -e ""
  echo -e "You can control the service with:"
  echo -e "  sudo systemctl start bird-inference.service"
  echo -e "  sudo systemctl stop bird-inference.service"
  echo -e "  sudo systemctl restart bird-inference.service"
  echo -e "  sudo systemctl status bird-inference.service"
  echo -e ""
  echo -e "View logs with:"
  echo -e "  journalctl -u bird-inference.service -f"
  echo -e "${GREEN}====================================${NC}"
}

# Run the deployment steps
main() {
  check_jetson
  setup_directories
  install_dependencies
  configure_server
  setup_service
  setup_cloudflare
  test_server
  show_summary
  
  echo -e "\n${GREEN}Deployment completed successfully!${NC}"
}

# Execute the main function
main 