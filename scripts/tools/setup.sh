#!/bin/bash
# Setup script for Bird Camera project on Raspberry Pi

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Function to print section headers
print_header() {
    echo -e "\n${BOLD}${BLUE}$1${RESET}"
    echo -e "${BLUE}$(printf '=%.0s' $(seq 1 ${#1}))${RESET}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${RESET}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${RESET}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}! $1${RESET}"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    print_header "Checking System"
    
    if [ -f /sys/firmware/devicetree/base/model ]; then
        model=$(cat /sys/firmware/devicetree/base/model)
        if [[ $model == *"Raspberry Pi"* ]]; then
            print_success "Running on $model"
            return 0
        else
            print_error "Not running on a Raspberry Pi (found: $model)"
            return 1
        fi
    else
        print_error "Not running on a Raspberry Pi (model file not found)"
        return 1
    fi
}

# Check camera setup
check_camera() {
    print_header "Checking Camera"
    
    if command -v vcgencmd &> /dev/null; then
        camera_status=$(vcgencmd get_camera)
        if [[ $camera_status == *"supported=1 detected=1"* ]]; then
            print_success "Camera detected"
            
            # Check for camera interfaces
            if [[ $camera_status == *"libcamera interfaces=1"* ]]; then
                print_success "Libcamera interfaces available"
            else
                print_warning "No libcamera interfaces available"
            fi
        else
            print_error "Camera not detected"
            print_warning "Camera status: $camera_status"
            return 1
        fi
    else
        print_error "vcgencmd not available"
        return 1
    fi
    
    return 0
}

# Check and enable camera in config
setup_camera_config() {
    print_header "Setting up Camera Configuration"
    
    # Check if camera is enabled in raspi-config
    if command -v raspi-config &> /dev/null; then
        camera_enabled=$(sudo raspi-config nonint get_camera)
        if [ "$camera_enabled" = "0" ]; then
            print_success "Camera is enabled in raspi-config"
        else
            print_warning "Camera is not enabled in raspi-config"
            echo "Enabling camera..."
            sudo raspi-config nonint do_camera 0
            print_success "Camera enabled"
        fi
    else
        print_warning "raspi-config not available, skipping camera enable check"
    fi
    
    # Check for camera dtoverlay in config.txt
    if grep -q "^dtoverlay=imx708" /boot/config.txt; then
        print_success "IMX708 camera configuration found in /boot/config.txt"
    elif grep -q "^dtoverlay=imx219" /boot/config.txt; then
        print_success "IMX219 camera configuration found in /boot/config.txt"
    else
        print_warning "No camera dtoverlay found in /boot/config.txt"
        
        # Try to detect camera model
        if dmesg | grep -q "imx708"; then
            print_success "Detected IMX708 camera module"
            camera_model="imx708"
        elif dmesg | grep -q "imx219"; then
            print_success "Detected IMX219 camera module"
            camera_model="imx219"
        else
            print_warning "Could not detect camera model, defaulting to IMX708"
            camera_model="imx708"
        fi
        
        # Add camera configuration
        echo "Adding camera configuration to /boot/config.txt..."
        echo -e "\n# Camera settings\ndtoverlay=$camera_model" | sudo tee -a /boot/config.txt > /dev/null
        print_success "Camera configuration added"
        print_warning "A reboot is required for changes to take effect"
    fi
}

# Install required packages
install_packages() {
    print_header "Installing Required Packages"
    
    # Update package lists
    echo "Updating package lists..."
    sudo apt update
    
    # Install required packages
    echo "Installing required packages..."
    sudo apt install -y python3-pip python3-venv libcamera-dev python3-picamera2 python3-opencv
    
    if [ $? -eq 0 ]; then
        print_success "System packages installed"
    else
        print_error "Failed to install system packages"
        return 1
    fi
    
    return 0
}

# Set up Python virtual environment
setup_venv() {
    print_header "Setting up Python Virtual Environment"
    
    # Check if venv exists
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Removing existing virtual environment..."
            rm -rf venv
        else
            print_success "Using existing virtual environment"
            return 0
        fi
    fi
    
    # Create virtual environment
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        return 1
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Install requirements
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
    
    return 0
}

# Set up systemd service
setup_service() {
    print_header "Setting up Systemd Service"
    
    # Check if systemd directory exists
    if [ ! -d "systemd" ]; then
        print_error "Systemd directory not found"
        return 1
    fi
    
    # Check if service file exists
    if [ ! -f "systemd/bird_camera.service" ]; then
        print_error "Service file not found"
        return 1
    fi
    
    # Copy service file
    echo "Copying service file..."
    sudo cp systemd/bird_camera.service /etc/systemd/system/
    
    if [ $? -eq 0 ]; then
        print_success "Service file copied"
    else
        print_error "Failed to copy service file"
        return 1
    fi
    
    # Set correct permissions
    sudo chmod 644 /etc/systemd/system/bird_camera.service
    
    # Reload systemd
    echo "Reloading systemd..."
    sudo systemctl daemon-reload
    
    # Enable service
    echo "Enabling service..."
    sudo systemctl enable bird_camera.service
    
    if [ $? -eq 0 ]; then
        print_success "Service enabled"
    else
        print_error "Failed to enable service"
        return 1
    fi
    
    print_warning "The service will start on next boot"
    read -p "Do you want to start the service now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Starting service..."
        sudo systemctl start bird_camera.service
        
        if [ $? -eq 0 ]; then
            print_success "Service started"
            echo "Check service status with: sudo systemctl status bird_camera.service"
        else
            print_error "Failed to start service"
            return 1
        fi
    fi
    
    return 0
}

# Run tests
run_tests() {
    print_header "Running Tests"
    
    # Activate virtual environment if not already activated
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Run camera test
    echo "Testing camera..."
    python tools/test_camera.py
    
    if [ $? -eq 0 ]; then
        print_success "Camera test passed"
    else
        print_error "Camera test failed"
    fi
    
    # Run PIR test
    echo -e "\nTesting PIR sensor..."
    echo "This will run for 10 seconds. Wave your hand in front of the sensor."
    python tools/test_pir.py --duration 10
    
    if [ $? -eq 0 ]; then
        print_success "PIR test completed"
    else
        print_error "PIR test failed"
    fi
}

# Main function
main() {
    print_header "Bird Camera Setup"
    echo "This script will set up the Bird Camera project on your Raspberry Pi."
    
    # Check if running on Raspberry Pi
    check_raspberry_pi
    if [ $? -ne 0 ]; then
        print_warning "Continuing anyway, but some features may not work"
    fi
    
    # Check camera
    check_camera
    
    # Setup camera config
    setup_camera_config
    
    # Install packages
    install_packages
    if [ $? -ne 0 ]; then
        print_error "Failed to install packages, exiting"
        exit 1
    fi
    
    # Setup virtual environment
    setup_venv
    if [ $? -ne 0 ]; then
        print_error "Failed to set up virtual environment, exiting"
        exit 1
    fi
    
    # Ask if user wants to set up service
    read -p "Do you want to set up the systemd service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_service
    fi
    
    # Ask if user wants to run tests
    read -p "Do you want to run tests? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    print_header "Setup Complete"
    echo "The Bird Camera project has been set up successfully."
    echo -e "\nTo manually start the application:"
    echo "  source venv/bin/activate"
    echo "  python src/main.py"
    
    # Check if reboot is needed
    if grep -q "^dtoverlay=.*" /boot/config.txt && ! grep -q "^dtoverlay=.*" <(dmesg | grep -i dtoverlay); then
        print_warning "A reboot is required for camera changes to take effect"
        read -p "Do you want to reboot now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Rebooting..."
            sudo reboot
        fi
    fi
}

# Run main function
main 