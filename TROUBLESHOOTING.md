# Troubleshooting Guide

This document contains information about issues we encountered during development and testing of the Bird Camera project, along with solutions and workarounds.

## Camera Issues

### Memory Constraints

**Problem:** When using OpenCV to access the camera, processes were being killed (exit code 137) due to insufficient memory.

**Diagnosis:**
- The Raspberry Pi has limited RAM (229MB total, ~90MB available)
- OpenCV camera operations are memory intensive
- The v4l2 driver (bcm2835 mmal) may have memory management issues

**Solutions:**
1. Use picamera2 instead of OpenCV for camera operations
2. If using OpenCV is necessary:
   - Reduce resolution (320x240 instead of higher resolutions)
   - Use simpler pixel formats (YUYV instead of MJPEG)
   - Increase swap space:
     ```
     sudo dphys-swapfile swapoff
     sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
     sudo dphys-swapfile setup
     sudo dphys-swapfile swapon
     ```

### Camera Detection Issues

**Problem:** Camera was showing as detected in hardware but not working with libraries.

**Diagnosis:**
- Mismatch between camera module type in configuration and actual hardware
- Multiple camera stacks installed (legacy v4l2 and newer libcamera)
- Incorrect dtoverlay settings in /boot/config.txt

**Solutions:**
1. Check camera module type:
   ```
   dmesg | grep -i camera
   ```
   Look for camera module ID (e.g., imx708, imx219)

2. Update /boot/config.txt with correct dtoverlay:
   ```
   # For IMX708 (Raspberry Pi Camera Module 3)
   dtoverlay=imx708
   
   # For IMX219 (Raspberry Pi Camera Module V2)
   dtoverlay=imx219
   ```

3. Clean up camera configuration:
   ```
   sudo sed -i '/# Camera settings/d' /boot/config.txt
   sudo sed -i '/# Enable camera/d' /boot/config.txt
   ```
   Then add the correct configuration.

## PIR Sensor Issues

**Problem:** PIR sensor not detecting motion or giving inconsistent readings.

**Diagnosis:**
- Incorrect GPIO pin configuration
- Insufficient warm-up time
- Incorrect pull-up/pull-down resistor configuration
- Hardware wiring issues

**Solutions:**
1. Allow sufficient warm-up time (30-60 seconds):
   ```python
   import time
   print("PIR sensor warming up...")
   time.sleep(60)  # Wait for PIR to stabilize
   print("Ready")
   ```

2. Try both pull-up and pull-down configurations:
   ```python
   # Pull-down (default HIGH when motion detected)
   GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   
   # Pull-up (default LOW when motion detected)
   GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   ```

3. Test with direct GPIO reading:
   ```python
   import RPi.GPIO as GPIO
   import time
   
   PIR_PIN = 17  # Adjust to your GPIO pin
   
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(PIR_PIN, GPIO.IN)
   
   try:
       while True:
           print(f"PIR state: {GPIO.input(PIR_PIN)}")
           time.sleep(1)
   except KeyboardInterrupt:
       GPIO.cleanup()
   ```

4. Verify physical connections:
   - VCC to 3.3V or 5V (check sensor specifications)
   - GND to ground
   - OUT to GPIO pin

## System Service Issues

**Problem:** Systemd service not starting properly or failing.

**Diagnosis:**
- Incorrect paths in service file
- Missing dependencies
- Permission issues

**Solutions:**
1. Check service status:
   ```
   sudo systemctl status bird_camera.service
   ```

2. View logs:
   ```
   sudo journalctl -u bird_camera.service
   ```

3. Verify service file permissions:
   ```
   sudo chmod 644 /etc/systemd/system/bird_camera.service
   ```

4. Reload systemd after changes:
   ```
   sudo systemctl daemon-reload
   ``` 