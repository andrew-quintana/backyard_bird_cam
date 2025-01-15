cmake_minimum_required(VERSION 3.15)

# Project name and version
project(RPiCameraModule LANGUAGES CXX VERSION 1.0)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Cross-compilation settings
if(CMAKE_CROSSCOMPILING)
    set(CMAKE_SYSTEM_NAME Linux)
    set(CMAKE_SYSTEM_PROCESSOR arm)
    set(CMAKE_C_COMPILER arm-linux-gnueabihf-gcc)
    set(CMAKE_CXX_COMPILER arm-linux-gnueabihf-g++)
    message(STATUS "Cross-compiling for Raspberry Pi")
endif()

# Enable warnings and optimizations
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    add_compile_options(-Wall -Wextra -Wpedantic -O0 -g)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -O3)
endif()

# Find libcamera
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBCAMERA REQUIRED libcamera)

if(NOT LIBCAMERA_FOUND)
    message(FATAL_ERROR "libcamera not found. Please ensure the Docker image includes it.")
endif()

include_directories(${LIBCAMERA_INCLUDE_DIRS})
link_directories(${LIBCAMERA_LIBRARY_DIRS})
add_definitions(${LIBCAMERA_CFLAGS_OTHER})

# Find OpenCV
find_package(OpenCV REQUIRED)

if(NOT OpenCV_FOUND)
    message(FATAL_ERROR "OpenCV not found. Please install OpenCV or specify its location.")
endif()

# Include OpenCV headers
include_directories(${OpenCV_INCLUDE_DIRS})

# Add the executable
add_executable(rpi_camera_app
    src/hardware/rpi_camera_module3.cpp
    src/main.cpp
)

# Link libraries
target_link_libraries(rpi_camera_app
    ${LIBCAMERA_LIBRARIES}
    ${OpenCV_LIBS}
    pthread
)

# Install the executable
install(TARGETS rpi_camera_app RUNTIME DESTINATION bin)

# Print summary
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Cross-compiling: ${CMAKE_CROSSCOMPILING}")