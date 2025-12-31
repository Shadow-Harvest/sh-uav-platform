# Base image: ROS2 Humble with desktop tools
FROM osrf/ros:humble-desktop-full

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install core dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
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
    # ArduPilot SITL dependencies
    python3-dev \
    python3-opencv \
    python3-wxgtk4.0 \
    python3-matplotlib \
    python3-lxml \
    python3-pygame \
    libxml2-dev \
    libxslt1-dev \
    # Network debugging
    netcat-openbsd \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    py-trees \
    python-statemachine \
    transforms3d \
    pytest \
    pytest-cov \
    ruff \
    black \
    flake8 \
    # ArduPilot Python dependencies
    pymavlink \
    MAVProxy \
    pexpect \
    future \
    empy==3.3.4 \
    pyserial \
    dronecan

# Install MAVROS geographiclib datasets
RUN /opt/ros/humble/lib/mavros/install_geographiclib_datasets.sh

# Clone and build ArduPilot SITL
ENV ARDUPILOT_HOME=/opt/ardupilot
RUN git clone --depth 1 --recurse-submodules https://github.com/ArduPilot/ardupilot.git ${ARDUPILOT_HOME} \
    && cd ${ARDUPILOT_HOME} \
    && ./waf configure --board sitl \
    && ./waf copter

# Add ArduPilot to PATH
ENV PATH="${ARDUPILOT_HOME}/Tools/autotest:${PATH}"

# Setup workspace
WORKDIR /ws
RUN mkdir -p src

# Source ROS2 on bash startup
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc \
    && echo "source /ws/install/setup.bash 2>/dev/null || true" >> ~/.bashrc

# Default command
CMD ["/bin/bash"]
