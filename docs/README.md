# Backyard Bird Cam Documentation

Welcome to the Backyard Bird Cam project! This system enables automated bird detection, photo capture, and transfer using a Raspberry Pi and a PIR motion sensor. The project is designed for easy setup and operation on both Mac and Windows environments.

## Quick Start

- **For full Raspberry Pi setup and photo transfer instructions, see:**
  - [`README_pi_camera_setup.md`](./README_pi_camera_setup.md)

## Project Structure

- `pi_bird_cam/` — All Raspberry Pi camera and sensor scripts
- `nano_inference_server/` — (If present) Jetson Nano or inference server code
- `scripts/` — Utility and deployment scripts
- `docs/` — Documentation (this folder)
- `data/` — Photo and data storage

## Features
- Motion-triggered, high-res photo capture
- Automatic or manual photo transfer to your computer (Mac/Windows)
- Easy installation and operation
- Customizable camera and sensor parameters

## Documentation
- **Pi Camera Setup & Photo Transfer:** [`README_pi_camera_setup.md`](./README_pi_camera_setup.md)
- **Other guides and troubleshooting:** See additional markdown files in this folder

## Contributing
- Please use feature branches for new work (see [Git SOP](https://github.com/andrew-quintana/prompt_sop/blob/main/git_testing_protocol.md))
- Submit pull requests to the `integration` branch

---

For any questions or issues, please refer to the setup guide or open an issue on GitHub. 