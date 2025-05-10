#!/bin/bash
# Deployment script for Jetson Nano inference server
# This script transfers the necessary files and sets up the server on the Jetson Nano

set -e  # Exit on error

# Configuration
JETSON_USER="qnest"
JETSON_HOST="192.168.5.164"
JETSON_ALIAS="jetson"
TARGET_DIR="/home/${JETSON_USER}/projects/nano_inference_server"
LOCAL_FILES=("jetson_compatibility.py" "jetson_server.py" "test_jetson_imports.py" "setup_tensorflow_jetson.sh")

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${GREEN}===== $1 =====${NC}\n"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Check if we can connect to the Jetson
print_header "Checking connection to Jetson Nano"
if ! ssh -q -o BatchMode=yes -o ConnectTimeout=5 $JETSON_ALIAS exit; then
    print_error "Cannot connect to Jetson Nano. Check your SSH configuration and connection."
    echo "Make sure the Jetson Nano is powered on and your SSH alias is configured."
    echo "Example ~/.ssh/config entry:"
    echo "Host jetson"
    echo "    HostName 192.168.5.164"
    echo "    User qnest"
    echo "    IdentityFile ~/.ssh/id_rsa"
    exit 1
fi
echo "Connection to Jetson Nano successful."

# Transfer files
print_header "Transferring files to Jetson Nano"
for file in "${LOCAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Transferring $file..."
        scp "$file" $JETSON_ALIAS:$TARGET_DIR/
    else
        print_error "File $file not found. Skipping."
    fi
done

# Make scripts executable
print_header "Setting up files on Jetson Nano"
ssh $JETSON_ALIAS "cd $TARGET_DIR && chmod +x *.sh *.py"

# Create a startup script
print_header "Creating startup script"
ssh $JETSON_ALIAS "cat > $TARGET_DIR/start_jetson_server.sh << 'EOF'
#!/bin/bash
# Startup script for Jetson Nano inference server

cd \$(dirname \$0)
export PYTHONPATH=\$PYTHONPATH:\$(pwd)

echo \"Starting Jetson Nano inference server...\"
LOG_FILE=\"./jetson_server.log\"

# Default to development mode which is safer for testing
DEV_MODE=\"--dev-mode\"
if [ \"\$1\" == \"--production\" ]; then
    DEV_MODE=\"\"
    echo \"Running in production mode\"
fi

# Run the server
python3 jetson_server.py \$DEV_MODE \$@ 2>&1 | tee \$LOG_FILE
EOF"

ssh $JETSON_ALIAS "chmod +x $TARGET_DIR/start_jetson_server.sh"

# Run the test script to verify imports
print_header "Running tests to verify packages"
ssh $JETSON_ALIAS "cd $TARGET_DIR && python3 test_jetson_imports.py" || {
    print_warning "Tests showed some issues. You may need to install TensorFlow."
    echo "You can run the TensorFlow installation script by running:"
    echo "ssh $JETSON_ALIAS \"cd $TARGET_DIR && ./setup_tensorflow_jetson.sh\""
}

# Provide instructions to start the server
print_header "Deployment complete"
echo "To start the inference server, run:"
echo "ssh $JETSON_ALIAS \"cd $TARGET_DIR && ./start_jetson_server.sh\""
echo ""
echo "To install TensorFlow for Jetson (if needed), run:"
echo "ssh $JETSON_ALIAS \"cd $TARGET_DIR && ./setup_tensorflow_jetson.sh\""
echo ""
echo "To test the server after starting it, run:"
echo "curl http://$JETSON_HOST:5000/health" 