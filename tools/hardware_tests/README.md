# Hardware Test Tools

This directory contains tools for testing and debugging hardware components of the backyard bird camera system.

## Tools

### PIR Sensor Tests

- **check_pir_directly.py**: Simple script to directly test the PIR sensor's GPIO pin and observe its raw output.
  ```
  python check_pir_directly.py --pin 17 --interval 0.5 --duration 30
  ```

- **check_inverted_pir.py**: Tests PIR sensor with different configurations to handle sensors with inverted logic.
  ```
  python check_inverted_pir.py --pin 17 --pullup --interval 0.5 --duration 30
  ```

- **long_pir_warmup.py**: Tests PIR sensor with an extended warm-up period which some sensors require.
  ```
  python long_pir_warmup.py --pin 17 --warmup 120 --duration 60
  ```

## Troubleshooting Tips

1. **No sensor response**: Try different GPIO pins, check wiring connections, or test with pull-up resistor.

2. **Inconsistent readings**: Some PIR sensors need a long warm-up period (2-3 minutes) to stabilize.

3. **Always high/low**: Check if the sensor logic is inverted or if there are wiring issues. 