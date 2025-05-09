# Final Hardware Testing for Bird Camera System

## Equipment Testing Checklist

### 1. PIR Sensor Calibration and Validation
- **Distance Testing**
  - Test detection at 1m, 2m, 3m, 5m distances
  - Verify sensitivity in direct line-of-sight vs. angles
  - Document effective detection zone

- **False Positive Testing**
  - Test in direct sunlight/changing light conditions
  - Test with simulated wind/moving foliage
  - Monitor for 24-hour period, log all triggers

- **Power Consumption**
  - Measure baseline current draw
  - Measure peak current during activation
  - Test with various warmup periods (15s, 30s, 60s)

### 2. Camera Module Testing

- **Image Quality Assessment**
  - Test in various lighting conditions (dawn, midday, dusk, night)
  - Evaluate optimal focus distance for bird feeder/bath
  - Compare resolution settings for quality vs. storage tradeoff

- **Performance Metrics**
  - Measure capture delay (trigger to saved image)
  - Test maximum capture rate (consecutive photos)
  - Measure power draw during active capture

- **Environmental Testing**
  - Test in high humidity conditions
  - Verify temperature range (early morning vs. midday)
  - Test with direct sunlight on camera module

### 3. Power System Verification

- **Battery Life (if applicable)**
  - Full charge to depletion test
  - Average runtime with normal trigger frequency
  - Standby time with no motion events

- **Solar Charging (if applicable)**
  - Charge rate in direct sun vs. partial cloud
  - Net power gain/loss over 24-hour cycle
  - Recovery time from depleted state

- **Power Stability**
  - Test for brown-outs during peak activity
  - Monitor for voltage drops affecting sensor reliability
  - Verify clean shutdown on low power

### 4. Enclosure and Physical Setup

- **Weather Resistance**
  - Water spray test (simulated light rain)
  - Dust ingress inspection after outdoor placement
  - Temperature inside enclosure vs. ambient

- **Mounting Stability**
  - Vibration test to ensure no false triggers
  - Wind resistance testing
  - Camera angle stability over time

- **Accessibility**
  - Ease of maintenance access
  - SD card removal/insertion without disruption
  - Cable strain relief effectiveness

## System Integration Testing

### 1. End-to-End Workflow Validation

- **Motion to Capture Pipeline**
  - Measure total latency (motion to saved image)
  - Test with rapid sequential motion events
  - Verify proper logging of events

- **24-Hour Continuous Operation**
  - Monitor for system stability
  - Verify no memory leaks or resource depletion
  - Confirm reliable startup after power cycle

- **Storage Management**
  - Test auto-cleanup of old images
  - Verify proper file rotation
  - Confirm no storage exhaustion errors

### 2. Network Integration (if applicable)

- **WiFi Reliability**
  - Signal strength at installation location
  - Connection recovery after outage
  - Power impact of wireless transmission

- **Upload Performance**
  - Success rate of cloud uploads
  - Bandwidth usage metrics
  - Queue management during offline periods

## Final Installation Checklist

### 1. Positioning Optimization
- **Field of View Confirmation**
  - Camera captures entire target area
  - PIR sensor covers approach paths
  - No blind spots in coverage

- **Background Assessment**
  - Clean background for better bird visibility
  - Minimal moving elements to reduce false triggers
  - Good contrast for bird identification

### 2. Final Calibration
- **Optimal Sensitivity Setting**
  - Balance between catching events vs. false positives
  - Adjusted based on installation distance
  - Specific to actual environment conditions

- **Image Settings Tuning**
  - Exposure compensation for lighting conditions
  - White balance appropriate for location
  - Resolution and quality appropriate for upload bandwidth

### 3. Documentation and Baseline
- **Installation Documentation**
  - Photos of final setup
  - Exact position measurements
  - Angle of camera and sensor

- **Baseline Performance Metrics**
  - Average daily motion events
  - False positive rate
  - Average battery life / power consumption 