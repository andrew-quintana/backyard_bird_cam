#include "camera.hpp"
#include <iostream>
#include <fstream>

Camera::Camera() {}

Camera::~Camera() {
    if (camera.isOpened()) {
        camera.release();
    }
}

bool Camera::initialize() {
    // open the camera
    if (!camera.open()) {
        std::cerr << "Error: Unable to open the camera." << std::endl;
        return false;
    }

    std::cout << "Camera initialized successfully." << std::endl;
    return true;
}

bool Camera::captureImage(const std::string& filename) {
    if (!camera.isOpened()) {
        std::cerr << "Error: Camera is not initialized." << std::endl;
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
        std::cerr << "Error: Unable to open file for writing: " << filename << std::endl;
        delete[] data;
        return false;
    }

    outFile << "P6\n" << camera.getWidth() << " " << camera.getHeight() << " 255\n";
    outFile.write(reinterpret_cast<char*>(data), camera.getImageTypeSize(raspicam::RASPICAM_FORMAT_RGB));

    std::cout << "Image saved to: " << filename << std::endl;

    // Free allocated memory
    delete[] data;
    return true;
}