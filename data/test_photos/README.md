# Camera Test Suite

This directory contains test photos taken with different camera settings to help determine the optimal configuration for the bird camera.

## How to Use the Script

You can run the test script from the main project directory with:

```
./scripts/camera_test_suite.py
```

This will take a series of photos with different settings and save them to this directory with the settings overlaid on each image for easy comparison.

### Options

- `--output/-o`: Specify a different output directory (default: `data/test_photos`)
- `--resolution/-r`: Set resolution preset (`low`, `medium`, `high`, `full`) (default: `medium`)
- `--profiles/-p`: Choose specific profiles to test (default: `all`)

Examples:

```
# Test only white balance settings at high resolution
./scripts/camera_test_suite.py --resolution high --profiles tungsten daylight cloudy

# Test low light settings with full resolution
./scripts/camera_test_suite.py --resolution full --profiles low_light
```

## Raspberry Pi Camera Capabilities

The Raspberry Pi camera has the following capabilities:

### Auto-focusing (for cameras with motorized focus)

- **Auto focus modes**: `auto` (one-time), `continuous` (constantly adjusts), `manual`
- **Focus ranges**: `normal`, `macro` (close-up), `full`
- **Manual focus control**: Setting lens position from 0.0 (infinity) to higher values (closer focus)

### Exposure Control

- **Shutter speed**: Programmable from 100µs (1/10,000s) to longer exposures
  - Camera Module 3 (IMX708): Max ~112 seconds
  - HQ Camera (IMX477): Max ~670 seconds
  - Camera Module 2 (IMX219): Max ~11.7 seconds
- **ISO/Gain**: Controlled with `--gain` parameter (higher values = brighter but noisier)
- **Exposure modes**: `normal`, `sport` (prioritizes faster shutter speeds)
- **Exposure compensation (EV)**: From -10 to +10 (default 0)
- **Metering modes**: `centre`, `spot`, `average`, `custom`

### White Balance

- **Auto white balance modes**:
  - `auto`: General-purpose (2500K-8000K)
  - `incandescent`: Indoor warm lighting (2500K-3000K)
  - `tungsten`: Tungsten lighting (3000K-3500K)
  - `fluorescent`: Fluorescent lighting (4000K-4700K)
  - `indoor`: General indoor (3000K-5000K)
  - `daylight`: Outdoor sunny (5500K-6500K)
  - `cloudy`: Outdoor cloudy (7000K-8500K)

### Image Quality Controls

- **Resolution**: Configurable up to sensor native resolution
- **Quality**: JPEG compression quality (0-100)
- **Sharpness**: Adjustable (0-2.0, default 1.0)
- **Contrast**: Adjustable (0-2.0, default 1.0)
- **Brightness**: Adjustable (-1.0 to 1.0, default 0.0)
- **Saturation**: Adjustable (0-2.0, default 1.0)
- **Image effects**: Horizontal/vertical flip, rotation
- **Denoise modes**: Various noise reduction options

### Note About Aperture

The Raspberry Pi cameras have a fixed aperture, so aperture cannot be adjusted like on a DSLR camera. Instead, exposure is controlled through shutter speed and gain/ISO.

## Common Settings for Bird Photography

1. **Fast Movement**: Use `fast_shutter` profile with faster shutter speeds (1/1000s) to freeze motion
2. **General Birdwatching**: Use `standard` or `high_detail` profiles
3. **Low Light**: Use `low_light` profile with longer exposure and higher gain
4. **Vibrant Colors**: Use `vivid` profile to enhance feather colors 