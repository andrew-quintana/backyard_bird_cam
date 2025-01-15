#include "hardware/rpi_camera_module3.h"
#include <iostream>

int main() {
    RPiCameraModule3 camera;

    if (!camera.initialize()) {
        std::cerr << "Failed to initialize the camera!" << std::endl;
        return 1;
    }

    if (!camera.takePicture()) {
        std::cerr << "Failed to take picture!" << std::endl;
        return 1;
    }

    std::cout << "Picture taken successfully!" << std::endl;
    return 0;
}