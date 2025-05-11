# Pi-Nano Connectivity Testing

These scripts help you verify connectivity between your Raspberry Pi and Jetson Nano during setup.

## Scripts Overview

1. **test_nano_server.py** - Run this on your Jetson Nano 
2. **test_pi_nano_connectivity.py** - Run this on your Raspberry Pi

## Usage Instructions

### On the Jetson Nano:

1. Run the test server:
   ```bash
   python3 test_nano_server.py
   ```
   
   This will start a simple HTTP server on port 8000 (by default) that will respond to connectivity tests.
   The server will display its IP address when started.

### On the Raspberry Pi:

1. Run the connectivity test, replacing `<NANO_IP>` with the IP address displayed by the Nano server:
   ```bash
   python3 test_pi_nano_connectivity.py <NANO_IP>
   ```
   
2. To check SSH connectivity as well:
   ```bash
   python3 test_pi_nano_connectivity.py <NANO_IP> --ssh
   ```

## Troubleshooting

If the connectivity test fails:

1. **Network Issues**: 
   - Ensure both devices are on the same network
   - Check that there's no firewall blocking the connections
   - Verify the IP address is correct

2. **Server Issues**:
   - Make sure the test server is running on the Nano
   - Check if the port is already in use (try a different port with `--port`)

3. **Nano Setup Issues**:
   - If the Nano is still setting up, some services might not be available yet
   - Check the Nano's logs for any error messages

## Testing Different Ports

If port 8000 is already in use:

- On the Nano: `python3 test_nano_server.py --port 8080`
- On the Pi: `python3 test_pi_nano_connectivity.py <NANO_IP> --port 8080` 