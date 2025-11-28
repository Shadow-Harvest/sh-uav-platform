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


### Troubleshooting:
# When MAVROS can't connect to SITL:
```
// specify out like this
sim_vehicle.py -v ArduCopter --console --map --out=udp:0.0.0.0:14550
```