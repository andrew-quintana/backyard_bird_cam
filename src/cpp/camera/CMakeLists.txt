# create a library for the camera module
add_library(camera
    camera.cpp
)

# link required libraries
target_link_libraries(camera
    raspicam
)

# specify include directories for the camera module
target_include_directories(camera PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})