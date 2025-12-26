# Base image: ROS2 Humble with desktop tools
FROM osrf/ros:humble-desktop-full

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# GPU support (used when available, ignored otherwise)
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute

# Install core dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    # Gazebo and ROS integration
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    # MAVROS
    ros-humble-mavros \
    ros-humble-mavros-extras \
    # Vision
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-camera-info-manager \
    # Behavior trees
    ros-humble-behaviortree-cpp \
    # TF and geometry
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    # Utilities
    git \
    wget \
    curl \
    vim \
    htop \
    mesa-utils \
    # For headless testing
    xvfb \
    # ArduPilot SITL dependencies
    python3-dev \
    python3-opencv \
    python3-wxgtk4.0 \
    python3-matplotlib \
    python3-lxml \
    python3-pygame \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    py-trees \
    python-statemachine \
    transforms3d \
    pytest \
    pytest-cov \
    ruff \
    black

# Install MAVROS geographiclib datasets
RUN /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh

# Setup workspace
WORKDIR /ws
RUN mkdir -p src

# Source ROS2 on bash startup
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ws/install/setup.bash 2>/dev/null || true" >> ~/.bashrc

# Default command
CMD ["/bin/bash"]