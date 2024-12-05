#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <raspicam/raspicam.h>
#include <string>

class Camera {
public:
    Camera();
    ~Camera();

    bool initialize();
    bool captureImage( const std::string& );

private:
    raspicam::RaspiCam camera;
    void logMessage(const std::string& message, const std::string& logType);
};

#endif // CAMERA_HPP