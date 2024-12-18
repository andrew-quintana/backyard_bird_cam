# specify the minimum cmake version
cmake_minimum_required(VERSION 3.10)

# project name
project(backyard_bird_cam)

# set c++ standard
set(CMAKE_CXX_STANDARD 17)

# enable testing
include(CTest)

# add subdirectories for cpp source files
add_subdirectory(src/cpp/camera)
add_subdirectory(src/cpp/logger)
add_subdirectory(tests/cpp_tests)

# find mutually used packages
find_package(Python3 REQUIRED)
find_package(pybind11 REQUIRED)

# Ensure Python from virtual environment is used
set(PYTHON_EXECUTABLE ${PROJECT_SOURCE_DIR}/.venv/bin/python)