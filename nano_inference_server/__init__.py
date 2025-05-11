"""
Nano Inference Server for Bird Detection

A modular inference server for the Jetson Nano that:
1. Monitors directories for new bird images
2. Runs detection and classification models
3. Stores and serves results through a web interface
4. Provides a REST API for integration

This package contains the following modules:
- inference: Model loading and inference
- monitoring: Directory monitoring for new images
- storage: Result storage and retrieval
- api: Web server and REST API
"""

__version__ = "0.1.0"
__author__ = "Backyard Bird Cam Team" 