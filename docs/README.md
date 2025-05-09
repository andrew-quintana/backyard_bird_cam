# Bird Camera Project Documentation

Welcome to the Bird Camera project documentation. This directory contains comprehensive guides and documentation for all aspects of the project.

## Quick Links

- [Project Roadmap](project_roadmap.md) - Overall project plan and current status
- [Hardware Testing Guide](hardware_testing_guide.md) - Comprehensive guide for testing and calibrating hardware
- [Cloud Integration Guide](cloud_integration_guide.md) - How to integrate with cloud services for storage and UI

## Project Overview

The Bird Camera project uses a Raspberry Pi with a camera module and PIR motion sensor to capture photos of birds. It can run standalone or integrate with cloud services for storage, machine learning classification, and web-based viewing.

## Directory Structure

The project is organized into the following directories:

- `src/` - Main source code
  - `camera/` - Camera handling code
  - `sensors/` - Sensor interfaces (PIR motion sensor)
  - `config/` - Configuration management
  - `storage/` - Photo storage handling
  - `uploader/` - Cloud upload functionality
  - `inference/` - Machine learning integration

- `scripts/` - Helper scripts for installation and management
  - `service/` - systemd service files
  - `setup/` - System setup scripts
  - `tools/` - Utility tools

- `tests/` - Test files for all components

- `docs/` - Documentation (you are here)

## Getting Started

See the main [README.md](../README.md) at the project root for installation and getting started instructions. 