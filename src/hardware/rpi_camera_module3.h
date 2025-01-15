#ifndef RPI_CAMERA_MODULE3_H
#define RPI_CAMERA_MODULE3_H

#include <string>
#include <iomanip>
#include <iostream>
#include <memory>
#include <thread>

#include <libcamera/libcamera.h>

using namespace libcamera;
using namespace std::chrono_literals;


class RPiCameraModule3 {
public:
    RPiCameraModule3();
    ~RPiCameraModule3();

    bool initialize();
    bool takePicture();
    StreamRole getMode() const { return currentMode_; }
private:
    std::unique_ptr<CameraManager> cm_;
    std::shared_ptr<Camera> camera_;
    StreamConfiguration streamConfig_;
    libcamera::Stream *stream_ = nullptr; // Raw pointer for stream
    std::unique_ptr<FrameBufferAllocator> bufferAllocator_;
    std::vector<std::unique_ptr<FrameBuffer>> buffers_;
    StreamRole currentMode_ = StreamRole::StillCapture;


    bool configureCamera();
    bool configureBufferAllocator();
    bool requestComplete( Request *request );
};

std::string getTime();

#endif // RPI_CAMERA_MODULE3_H