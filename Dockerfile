# Use an ARM-compatible base image for Raspberry Pi
FROM --platform=$BUILDPLATFORM arm64v8/debian:bullseye-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    meson \
    ninja-build \
    pkg-config \
    git \
    python3-pip \
    python3-jinja2 \
    libboost-dev \
    libgnutls28-dev \
    libjpeg-dev \
    libtiff5-dev \
    libevent-dev \
    libunwind-dev \
    libdw-dev \
    libyaml-dev \
    python3-yaml \
    python3-ply \
    libopencv-dev \
    && apt-get clean

# Upgrade pip and install the latest version of Meson
RUN pip3 install --upgrade pip && \
    pip3 install meson==0.64.1

# Clone the libcamera repository and build it
RUN git clone https://git.libcamera.org/libcamera/libcamera.git /opt/libcamera && \
    cd /opt/libcamera && \
    meson setup build && \
    ninja -C build install

# Set the working directory for your application
WORKDIR /app

# Copy the source code and CMakeLists.txt into the container
COPY . .

# Debugging: List contents of /app
RUN ls -R /app

# Create a build directory and compile your application
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make

# Set the default command to run the application
CMD ["./build/rpi_camera_app"]