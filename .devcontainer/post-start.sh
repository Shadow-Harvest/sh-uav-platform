#!/bin/bash
# Post-start script for dev container

# Source ROS2 environment
source /opt/ros/humble/setup.bash

# Source workspace (if it exists)
if [ -f /ws/install/setup.bash ]; then
    source /ws/install/setup.bash
fi

echo "✅ Dev container environment ready!"
