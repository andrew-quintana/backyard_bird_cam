# Camera Test Tools

This directory contains tools for testing and calibrating the Raspberry Pi camera module.

## Tools

- **camera_test.py**: Basic test script to check if Picamera2 is installed and can initialize the camera.
  ```
  python camera_test.py
  ```

- **camera_test_lowres.py**: Tests the camera with low resolution (1280x720) to minimize memory usage.
  ```
  python camera_test_lowres.py
  ```

- **camera_test_highres.py**: Tests the camera with high resolution (native camera resolution, typically 4608x2592 for IMX708).
  ```
  python camera_test_highres.py
  ```

## Troubleshooting

### Memory Issues

If you encounter memory allocation errors like:
```
ERROR V4L2 v4l2_videodevice.cpp:1321 /dev/video0[16:cap]: Unable to request 2 buffers: Cannot allocate memory
```

It means you need to increase the GPU memory. Add this to `/boot/firmware/config.txt`:
```
gpu_mem=256
```

Then reboot the Raspberry Pi:
```
sudo reboot
```

### Camera Not Detected

If the camera is not detected:
1. Make sure the camera module is properly connected
2. Enable the camera in Raspberry Pi configuration:
   ```
   sudo raspi-config
   ```
   Navigate to "Interface Options" > "Camera" and enable it.

### Mock Camera Detection

If tests show "Mock Camera" output:
1. Make sure the Picamera2 library is installed:
   ```
   sudo apt update
   sudo apt install -y python3-libcamera python3-picamera2
   ```
2. Create a virtual environment with access to system packages:
   ```
   python3 -m venv venv --system-site-packages
   ``` 