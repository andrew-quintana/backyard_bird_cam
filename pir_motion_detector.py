#!/usr/bin/env python3
import pigpio
import time
import datetime
import os

# Configuration
PIR_PIN = 4                    # BCM pin number for PIR sensor
PHOTO_DIR = "data/photos"      # Directory to store photos
LOG_FILE = "motion_events.log" # Log file for motion events
COOLDOWN_TIME = 5              # Seconds to wait between motion detections

def log_event(message):
    """Log a message to both console and log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def take_photo():
    """Capture a photo using libcamera."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{PHOTO_DIR}/motion_{timestamp}.jpg"
    
    # Ensure directory exists
    os.makedirs(PHOTO_DIR, exist_ok=True)
    
    # Capture photo using libcamera-still
    cmd = f"libcamera-still -o {filename} --immediate"
    log_event(f"Capturing photo: {filename}")
    os.system(cmd)
    log_event(f"Photo saved: {filename}")
    
    return filename

def main():
    """Main function to monitor PIR sensor and capture photos on motion detection."""
    log_event("Starting PIR motion detection system")
    log_event(f"Using GPIO pin {PIR_PIN}")
    
    # Ensure the log file directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    try:
        # Connect to the pigpio daemon
        pi = pigpio.pi()
        if not pi.connected:
            log_event("Failed to connect to pigpio daemon. Try running 'sudo pigpiod' first.")
            return
        
        # Set pin mode
        pi.set_mode(PIR_PIN, pigpio.INPUT)
        
        log_event("PIR sensor initialized successfully")
        log_event("Sensor warming up (30 seconds)...")
        
        # Give the PIR sensor time to stabilize
        time.sleep(30)
        
        log_event("System ready - Monitoring for motion")
        
        last_motion_time = 0
        last_state = 0
        
        while True:
            # Read the current state
            current_state = pi.read(PIR_PIN)
            
            # Check if motion was detected (rising edge: 0->1)
            if current_state == 1 and last_state == 0:
                current_time = time.time()
                
                # Check if we're past the cooldown period
                if current_time - last_motion_time > COOLDOWN_TIME:
                    log_event("Motion detected!")
                    photo_path = take_photo()
                    last_motion_time = current_time
            
            # Update last state
            last_state = current_state
            
            # Small sleep to prevent CPU hogging
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        log_event("System stopped by user")
    except Exception as e:
        log_event(f"Error: {e}")
    finally:
        # Clean up
        if 'pi' in locals() and pi.connected:
            pi.stop()
            log_event("GPIO resources released")
        log_event("System shutdown complete")

if __name__ == "__main__":
    main() 