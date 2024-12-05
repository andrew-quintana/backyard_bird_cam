#include "camera/camera.hpp"
#include <gtest/gtest.h>
#include <fstream>

// helper function to check if a file exists
bool fileExists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}

// test the camera initialization
TEST(CameraTest, InitializeCameraSuccess) {
    Camera cam;

    // assuming the camera hardware is available, this should succeed
    EXPECT_TRUE(cam.initialize());
}

// test captureImage without initializing the camera
TEST(CameraTest, CaptureImageWithoutInitialization) {
    Camera cam;

    // captureImage should fail without initialization
    EXPECT_FALSE(cam.captureImage("test_image.ppm"));
}

// test successful image capture
TEST(CameraTest, CaptureImageSuccess) {
    Camera cam;
    ASSERT_TRUE(cam.initialize());

    // specify a test image file path
    std::string testImagePath = "test_image.ppm";

    // capture the image
    EXPECT_TRUE(cam.captureImage(testImagePath));

    // check if the image file was created
    EXPECT_TRUE(fileExists(testImagePath));

    // cleanup: remove the test image file
    std::remove(testImagePath.c_str());
}