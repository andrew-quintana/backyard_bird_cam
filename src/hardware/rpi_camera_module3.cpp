// much of this is based on simple-cam.cpp

#include "rpi_camera_module3.h"

#include <fstream>
#include <stdexcept>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <sstream>

#include <fcntl.h>
#include <sys/mman.h>
#include <opencv2/opencv.hpp>

using namespace libcamera;

RPiCameraModule3::RPiCameraModule3() {
    cm_ = std::make_unique<CameraManager>();
}

RPiCameraModule3::~RPiCameraModule3() {
    camera_->stop();
    bufferAllocator_->free(stream_);
    camera_->release();
    camera_.reset();
    cm_->stop();
}

bool RPiCameraModule3::initialize() {
    // start camera initialization
    if (cm_->start() != 0) {
        std::cerr << "Failed to start CameraManager!" << std::endl;
        return false;
    }

    // get list of cameras and inspect for failures
    auto cameras = cm_->cameras();
    if (cameras.empty()) {
        std::cerr << "No cameras detected!" << std::endl;
        return false;
    }
    else {
        std::cout << "Cameras detected:" << std::endl;
        for (auto const &camera : cameras)
            std::cout << camera->id() << std::endl;
    }

    // retrieve camera
    std::string cameraId = cameras[0]->id();
    camera_ = cm_->get(cameraId);
    if (!camera_) {
        std::cerr << "Failed to retrieve camera!" << std::endl;
        return false;
    }

    // acquire camera
    if (camera_->acquire()) {
        std::cerr << "Failed to acquire camera!" << std::endl;
        return false;
    }

    // connect requestCompleted signal to requestComplete slot
    camera_->requestCompleted.connect(this, &RPiCameraModule3::requestComplete);

    return configureCamera();
}

bool RPiCameraModule3::configureCamera() {
    // configure the camera for image capture (highest quality setup)
    std::cout << "Configuring camera..." << std::endl;
    
    // generate stream configuration
    std::unique_ptr<CameraConfiguration> config = camera_->generateConfiguration( { currentMode_ } );

    if (!config) {
        std::cerr << "Failed to generate camera configuration!" << std::endl;
        return false;
    }

    // get the stream configuration
    streamConfig_ = config->at(0);

    // the default size is set to the maximum supported resolution for the specified role
    unsigned int maxWidth = streamConfig_.size.width;
    unsigned int maxHeight = streamConfig_.size.height;

    // assign these values to your stream configuration
    streamConfig_.size.width = maxWidth;
    streamConfig_.size.height = maxHeight;

    // validate the updated configuration
    if (!config->validate()) {
        std::cerr << "ERROR: Failed to validate camera configuration." << streamConfig_.toString() << std::endl;
    }
    else {
        std::cout << "Validated viewfinder configuration is: " << streamConfig_.toString() << std::endl;
    }

    // finally, configure the camera with the updated configuration
    if (camera_->configure(config.get()) < 0) {
        std::cerr << "Failed to configure camera with the new settings!" << std::endl;
        return false;
    }

    return configureBufferAllocator();
}

bool RPiCameraModule3::configureBufferAllocator() {
    // free existing buffers
    if (bufferAllocator_) {
        bufferAllocator_->free(stream_);
    }

    // create new FrameBufferAllocator
    bufferAllocator_ = std::make_unique<FrameBufferAllocator>(camera_);
    if (!bufferAllocator_) {
        std::cerr << "failed to create FrameBufferAllocator!" << std::endl;
        return false;
    }

    // allocate frame buffers for the stream
    int ret = bufferAllocator_->allocate(stream_);
    if (ret < 0) {
        std::cerr << "failed to allocate frame buffers!" << std::endl;
        return false;
    }

    // retrieve the allocated buffers
    const auto &allocatedBuffers = bufferAllocator_->buffers(stream_);
    if (allocatedBuffers.empty()) {
        std::cerr << "no buffers allocated!" << std::endl;
        return false;
    }

    // store the buffers in the member variable
    buffers_.clear();
    for (const auto &buffer : allocatedBuffers) {
        buffers_.push_back(std::unique_ptr<FrameBuffer>(buffer.get()));
    }

    std::cout << "frame buffers allocated successfully!" << std::endl;
    return true;
}

bool RPiCameraModule3::takePicture() {
    std::cout << "Capturing image..." << std::endl;

    // setup stream instance and requests to be submitted to buffer
    stream_ = streamConfig_.stream();
    const std::vector<std::unique_ptr<FrameBuffer>> &buffers = bufferAllocator_->buffers(stream_);
    std::vector<std::unique_ptr<Request>> requests;

    // fill request vector by creating request instances from device and associate each to a buffer
    for (unsigned int i = 0; i < buffers.size(); ++i) {
        std::unique_ptr<Request> request = camera_->createRequest();
        if (!request)
        {
            std::cerr << "Can't create request" << std::endl;
            return -ENOMEM;
        }

        const std::unique_ptr<FrameBuffer> &buffer = buffers[i];
        int ret = request->addBuffer(stream_, buffer.get());
        if (ret < 0)
        {
            std::cerr << "Can't set buffer for request"
                << std::endl;
            return ret;
        }

        requests.push_back(std::move(request));
    }

    // submit requests and wait for completion
    if (camera_->start() < 0) {
        std::cerr << "Failed to start camera!" << std::endl;
        return false;
    }

    // queue requests to be processed
    // libcamera will execute event loop processing, otherwise use direct control via EventLoop
    for (std::unique_ptr<Request> &request : requests) {
        if (camera_->queueRequest(request.get()) < 0) {
            std::cerr << "Failed to queue request." << std::endl;
            return false;
        }
    }

    std::cout << "Image captured and processed." << std::endl;
    return true;
}


bool RPiCameraModule3::requestComplete(Request *request) {
    // check if completed
    if (request->status() != Request::RequestCancelled) {

        const Request::BufferMap &buffers = request->buffers();

        // inspect each completed buffer in request and access metadata
        for (auto bufferPair : buffers) {

            // get the buffer from the completed request
            FrameBuffer *buffer = bufferPair.second;

            // Ensure the buffer is valid
            if (buffer->planes().empty()) {
                std::cerr << "Buffer has no planes." << std::endl;
                continue;
            }

            // access the first plane of the buffer
            const libcamera::FrameBuffer::Plane &plane = buffer->planes()[0];
            int fd = plane.fd.get();
            size_t length = plane.length;

            // map the buffer into the application's address space
            void *mappedData = mmap(NULL, length, PROT_READ, MAP_SHARED, fd, 0);
            if (mappedData == MAP_FAILED) {
                std::cerr << "Failed to mmap buffer." << std::endl;
                continue;
            }

            // assuming the image is in YUV420 format; adjust as necessary
            int width = 1920;  // Replace with actual width
            int height = 1080; // Replace with actual height

            // create an OpenCV Mat from the YUV data
            cv::Mat yuvImage(height + height / 2, width, CV_8UC1, mappedData);

            // convert YUV to BGR (OpenCV uses BGR by default)
            cv::Mat bgrImage;
            cv::cvtColor(yuvImage, bgrImage, cv::COLOR_YUV2BGR_I420);

            // save the image as a JPEG file
            std::string filename = "captured_image.jpg";
            if (!cv::imwrite(filename, bgrImage)) {
                std::cerr << "Failed to save image." << std::endl;
            } else {
                std::cout << "Image saved as " << filename << std::endl;
            }

            // unmap the buffer
            if (munmap(mappedData, length) == -1) {
                std::cerr << "Failed to munmap buffer." << std::endl;
            }

        }

        // Re-queue the Request to the camera
        request->reuse(Request::ReuseBuffers);
        camera_->queueRequest(request);

        return true; 
    } else {
        std::cerr << "ERROR: Request failed with status: " << request->status() << std::endl;
        return false;
    }
    return true;
}

std::string getTime() {
    // Get the current time point from the system clock
    auto now = std::chrono::system_clock::now();

    // Convert to time_t to extract the calendar time
    std::time_t timeNow = std::chrono::system_clock::to_time_t(now);

    // Convert to milliseconds to extract the fractional seconds
    auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()
    ) % 1000;

    // Create a stringstream to format the timestamp
    std::stringstream timeStream;

    // Format the time part (YYYYMMDDHHMMSS)
    timeStream << std::put_time(std::localtime(&timeNow), "%Y%m%d%H%M%S");

    // Append milliseconds with leading zeros to ensure three digits
    timeStream << '.' << std::setfill('0') << std::setw(3) << milliseconds.count();

    // Return the formatted timestamp string
    return timeStream.str();
}