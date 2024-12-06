#include "camera.hpp"
#include "logger.hpp" // Include the logger for the LOG macro
#include <fstream>

Camera::Camera() {
    LOG("INFO", "camera", "Camera object created.");
}

Camera::~Camera() {
    if (camera.isOpened()) {
        camera.release();
        LOG("INFO", "camera", "Camera resources released.");
    }
}

bool Camera::initialize() {
    // Attempt to open the camera
    if (!camera.open()) {
        LOG("ERROR", "camera", "Unable to open the camera.");
        return false;
    }

    LOG("INFO", "camera", "Camera initialized successfully.");
    return true;
}

bool Camera::captureImage(const std::string& filename) {
    if (!camera.isOpened()) {
        LOG("ERROR", "camera", "Camera is not initialized.");
        return false;
    }

    // Capture an image
    camera.grab();

    // Allocate memory for image data
    unsigned char* data = new unsigned char[camera.getImageTypeSize(raspicam::RASPICAM_FORMAT_RGB)];
    camera.retrieve(data, raspicam::RASPICAM_FORMAT_RGB);

    // Save the image to a file
    std::ofstream outFile(filename, std::ios::binary);
    if (!outFile) {
        LOG("ERROR", "camera", "Unable to open file for writing: " + filename);
        delete[] data;
        return false;
    }

    // Write the image data to the file
    outFile << "P6\n" << camera.getWidth() << " " << camera.getHeight() << " 255\n";
    outFile.write(reinterpret_cast<char*>(data), camera.getImageTypeSize(raspicam::RASPICAM_FORMAT_RGB));
    LOG("INFO", "camera", "Image saved to: " + filename);

    // Free allocated memory
    delete[] data;
    return true;
}