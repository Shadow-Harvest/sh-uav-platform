# SH UAV Platform

Autonomous UAV platform built on ROS2.

## Development Environment

### Prerequisites

- Docker Desktop
- Make

### Quick Start
```bash
# Build Docker image (first time or after Dockerfile changes)
make docker-build

# Enter development container
make dev

# Build and run all tests
make test

# Build only
make build

# Clean build artifacts
make clean
```

### Architecture
```
Mac (host)                          Docker Container
────────────────────────────────────────────────────────────
~/Developer/.../sh-uav-platform/
├── src/  ◄──── mounted ────►  /ws/src/     (your code)
├── build/ ◄─── mounted ────►  /ws/build/   (build cache)
├── install/ ◄─ mounted ────►  /ws/install/ (built packages)
└── docker/                    
    ├── Dockerfile             ROS2 Humble + dependencies
    ├── compose.yml            Base configuration
    ├── compose.mac.yml        Mac overrides (no GPU)
    └── compose.gpu.yml        PC overrides (NVIDIA GPU)
```

### TDD Workflow
```bash
# Terminal 1: VS Code editing files on Mac

# Terminal 2: Stay in container for fast iteration
make dev
source /opt/ros/humble/setup.bash
source install/setup.bash

# Fast test commands inside container:
colcon build --packages-select <package_name>     # Build one package
pytest src/<package>/test/test_file.py            # Run one test file
pytest src/<package>/test/test_file.py::test_fn   # Run one test function
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all commands |
| `make dev` | Enter container shell |
| `make build` | Build ROS2 workspace |
| `make test` | Build and run all tests |
| `make sim` | Launch simulation (PC with GPU only) |
| `make docker-build` | Rebuild Docker image |
| `make clean` | Remove build artifacts |

## PC Setup (WSL2 with GPU)

### Prerequisites (one-time)
```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Install X11 utils for GUI
sudo apt-get install -y x11-xserver-utils
```

### Running SITL Test

**Terminal 1 — Start ArduPilot SITL:**
```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py -v ArduCopter --console --map --out=udp:0.0.0.0:14550
```

**Terminal 2 — Start ROS2 container with MAVROS:**
```bash
xhost +local:docker
make dev

# Inside container:
source /opt/ros/humble/setup.bash
ros2 launch mavros apm.launch fcu_url:=udp://:14550@host.docker.internal:14550
```

**Terminal 3 — Test commands:**
```bash
newgrp docker
docker exec -it $(docker ps -q) bash

# Inside container:
source /opt/ros/humble/setup.bash

# Check connection
ros2 topic echo /mavros/state --once
# Should show: connected: true

# Test flight
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{base_mode: 0, custom_mode: 'GUIDED'}"
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"
ros2 service call /mavros/cmd/takeoff mavros_msgs/srv/CommandTOL "{altitude: 3.0}"

# Land
ros2 service call /mavros/cmd/land mavros_msgs/srv/CommandTOL "{}"
```
