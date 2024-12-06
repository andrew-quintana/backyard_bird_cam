# Bird Camera Project

A Raspberry Pi-based bird camera system that uses C++ for camera and sensor control, Python for machine learning and cloud integration, and mjpg-streamer for live video streaming.

---

## **Features**
- Motion detection using a PIR sensor.
- Captures and processes images using C++.
- Runs a deployed ML model in Python for classification.
- Automatically uploads classified images to the cloud.
- Streams live video upon request via a browser.

## **Checkpoints**
### **ML Model Development & Training**
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1jj5cHTC-tGtNcy4WQIQU7NtI3_4wVIw5?usp=sharing)
- [X] Identify Dataset
- [X] Model Development
- [X] Model Tuning
- [ ] Hypertuning for Retraining Optimization
- [ ] New Species Scraping and Appending to Dataset
- [ ] Model Retraining Process (for new animals identified)

### **Setup**
- [ ] Raspberry Pi OS installed and updated.
- [ ] Camera module connected and tested (`raspistill` command).
- [ ] PIR sensor connected and functional (`gpiozero` test in Python).

### **Implementation**
- [ ] C++ code for motion-triggered camera capture completed.
- [ ] Python ML model integration for classification functional.
- [ ] Cloud upload script tested with credentials.

### **Streaming**
- [ ] mjpg-streamer installed and configured for browser access.
- [ ] Web interface created for live stream display.

### **Deployment**
- [ ] Project organized in recommended folder structure.
- [ ] Automated startup setup using `systemd` or `cron`.
- [ ] Tested full pipeline: motion detection → capture → classification → upload.