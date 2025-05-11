# Bird Camera System: Raspberry Pi Setup & Photo Transfer Guide

## 1. System Overview

- Uses a PIR motion sensor to detect birds
- Captures high-resolution photos in bursts
- Transfers photos to your computer (Mac or Windows)
- Can run automatically on Pi startup

---

## 2. Hardware Requirements

- Raspberry Pi (3, 4, or Zero 2W)
- Pi Camera Module (v2 or HQ)
- PIR motion sensor
- Power supply (5V/2.5A+ or battery)
- microSD card (16GB+ recommended)

---

## 3. Installation & Setup

### 3.1. Copy Files to Pi

```bash
scp -r * pi@YOUR_PI_IP:/home/pi/bird_cam/
```

### 3.2. SSH into Pi

```bash
ssh pi@YOUR_PI_IP
```

### 3.3. Install Dependencies

```bash
cd ~/bird_cam/scripts/setup
chmod +x install_bird_cam.sh
./install_bird_cam.sh
```

### 3.4. Reboot

```bash
sudo reboot
```

---

## 4. System Operation

### 4.1. Automatic Operation

- System starts on boot, detects motion, captures bursts, saves to `/home/pi/bird_cam/data/photos`.

### 4.2. Manual Control

```bash
sudo systemctl start bird_camera.service
sudo systemctl stop bird_camera.service
sudo systemctl status bird_camera.service
sudo journalctl -u bird_camera.service -f
sudo systemctl disable bird_camera.service  # Disable autostart
```

### 4.3. Camera Parameters

- 5 photos per burst, 0.05s sampling, 0.3s between photos, 3s cooldown.
- Change in `scripts/launch_bird_cam.sh` or `simple_pir_trigger.py`.

---

## 5. Photo Management & Transfer

### 5.1. Viewing Photos

- Use SFTP or SSH to browse/download from `/home/pi/bird_cam/data/photos`.

### 5.2. Transfer Photos to Computer

#### Option 1: Transfer Most Recent Photo

1. **Find your computer's IP:**
   - **Mac:** `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - **Windows (PowerShell):** `Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '127.*'}`

2. **Transfer script to Pi:**
   - **Mac:** `scp scripts/transfer_photo_to_mac.sh pi@YOUR_PI_IP:/home/pi/bird_cam/scripts/`
   - **Windows:** Use WinSCP or OpenSSH to copy the script.

3. **SSH into Pi and make script executable:**
   ```bash
   cd ~/bird_cam/scripts
   chmod +x transfer_photo_to_mac.sh
   ```

4. **Run the script:**
   ```bash
   ./transfer_photo_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP
   # Optionally: ./transfer_photo_to_mac.sh USERNAME IP /path/to/photos
   ```

#### Option 2: Sync All Photos

1. **Transfer script to Pi:** (as above, but use `sync_photos_to_mac.sh`)
2. **Make executable:**
   ```bash
   cd ~/bird_cam/scripts
   chmod +x sync_photos_to_mac.sh
   ```
3. **Run:**
   ```bash
   ./sync_photos_to_mac.sh YOUR_COMPUTER_USERNAME YOUR_COMPUTER_IP
   # Optionally: ./sync_photos_to_mac.sh USERNAME IP /path/to/photos
   ```

#### Customizing Destination

- Edit `MAC_DEST_DIR` in the script for your preferred location.
- For Windows with OpenSSH, use `/c/Users/YOUR_USERNAME/...`.

#### SSH Keys (Recommended)

```bash
ssh-keygen -t rsa
ssh-copy-id YOUR_COMPUTER_USERNAME@YOUR_COMPUTER_IP
ssh YOUR_COMPUTER_USERNAME@YOUR_COMPUTER_IP  # Test connection
```
- On Windows, you may need to manually copy the public key to `C:\Users\YOUR_USERNAME\.ssh\authorized_keys`.

#### Scheduling Automatic Transfers

```bash
crontab -e
# Add:
0 * * * * /home/pi/bird_cam/scripts/sync_photos_to_mac.sh USERNAME IP /path/to/photos >> /home/pi/bird_cam/logs/photo_sync.log 2>&1
```

---

## 6. Troubleshooting

- **Camera not working:** `vcgencmd get_camera` should show `supported=1 detected=1`
- **Black images:** Check camera ribbon cable
- **No motion detection:** Check PIR wiring (default GPIO4)
- **Too sensitive:** Adjust PIR potentiometer
- **Power issues:** Use adequate power supply
- **Battery drains:** Lower resolution or sampling rate

---

## 7. Customization

- **Change photo resolution:** Edit `initialize_camera()` in `simple_pir_trigger.py`
- **Change PIR pin:** Add `--pin X` in `launch_bird_cam.sh`
- **Other parameters:** Set in `launch_bird_cam.sh` or `simple_pir_trigger.py`

---

## 8. Notes for Windows Users

- Use WinSCP for GUI file transfer, or OpenSSH for command-line.
- Allow SSH through Windows firewall.
- Use `/c/Users/YOUR_USERNAME/...` for OpenSSH paths.

---

**This single document now covers setup, operation, photo transfer, troubleshooting, and customization for both Mac and Windows users.** 