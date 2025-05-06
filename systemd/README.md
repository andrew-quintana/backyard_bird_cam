# Systemd Service Files

This directory contains systemd service files for automatically starting the bird camera application at system boot.

## Files

- **bird_camera.service**: Systemd service file to run the bird camera application as a background service.

## Installation Instructions

1. Copy the service file to the systemd directory:
   ```
   sudo cp bird_camera.service /etc/systemd/system/
   ```

2. Reload systemd to recognize the new service:
   ```
   sudo systemctl daemon-reload
   ```

3. Enable the service to start at boot:
   ```
   sudo systemctl enable bird_camera.service
   ```

4. Start the service:
   ```
   sudo systemctl start bird_camera.service
   ```

## Service Management

- Check service status:
  ```
  sudo systemctl status bird_camera.service
  ```

- Stop the service:
  ```
  sudo systemctl stop bird_camera.service
  ```

- Restart the service:
  ```
  sudo systemctl restart bird_camera.service
  ```

- View logs:
  ```
  sudo journalctl -u bird_camera.service -f
  ``` 