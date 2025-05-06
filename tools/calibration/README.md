# Calibration Tools

This directory contains tools for calibrating and fine-tuning the various sensors and components of the backyard bird camera system.

## Tools

### PIR Sensor Calibration

- **calibrate_pir.py**: Tool for testing and calibrating the PIR motion sensor. It continuously polls the sensor and outputs its values to help determine optimal settings.
  ```
  python calibrate_pir.py --pin 17 --interval 0.1 --warmup 10 --debug
  ```

- **analyze_pir_data.py**: Analyzes PIR sensor data collected in CSV format to determine optimal thresholds for motion detection.
  ```
  python analyze_pir_data.py pir_data.csv --windows 0.5 1.0 2.0 5.0
  ```

## Example Usage

1. Collect calibration data:
   ```
   python calibrate_pir.py --csv --interval 0.1 --duration 60 > pir_data.csv
   ```

2. Analyze the collected data:
   ```
   python analyze_pir_data.py pir_data.csv
   ```

3. Based on analysis results, adjust settings in your config.json file. 