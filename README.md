# SH UAV Platform

> Autonomous UAV platform for ArUco marker search and approach missions, built on ROS2 Humble with ArduPilot SITL integration.

[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)](https://docs.ros.org/en/humble/)
[![ArduPilot](https://img.shields.io/badge/ArduPilot-Copter-green)](https://ardupilot.org/)
[![Python](https://img.shields.io/badge/Python-3.10-yellow)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)

---

## 📋 Project Overview

An enterprise-grade autonomous drone platform demonstrating modern robotics architecture patterns:

- **Mission**: Autonomous search, detection, and approach to ArUco markers
- **Approach**: Simulation-first TDD with seamless SITL → Hardware deployment path
- **Standards**: Designed following defense/aerospace patterns (clean architecture, state machines, behavior trees)

### Current Status

**Phase 1: Foundation** ✅ Complete
- ✅ Docker SITL environment
- ✅ MAVROS integration with ArduPilot
- ✅ Vehicle FSM and controller
- ✅ Takeoff/Land actions via NAV_TAKEOFF/NAV_LAND

**Phase 2-6: In Progress**
- 🚧 Perception pipeline (ArUco detection)
- 📋 Behavior tree framework
- 📋 Visual servoing approach
- 📋 Hardware deployment

[→ See detailed roadmap](documents/roadmap.md)

---

## 🎯 Key Features

### Architecture Highlights

- **Layered Architecture**: Clean separation between Mission → Planning → Control → HAL
- **State Management**: Safety-critical FSM for vehicle lifecycle + Behavior Trees for mission logic
- **ArduPilot Integration**: Native NAV_TAKEOFF/NAV_LAND with autonomous position hold
- **Test-Driven**: 80%+ coverage with unit, integration, and SITL tests
- **Docker-First**: Reproducible dev environment with hot-reload

### Technical Capabilities

- **Autonomous Takeoff/Land**: Via MAVROS service calls to ArduPilot
- **State Estimation**: Fused vehicle + target state for world model
- **Extensible Perception**: Plugin architecture for multiple detector types
- **Mission Execution**: py_trees-based behavior tree engine
- **Safety First**: FSM-enforced safety envelope with failsafe handling

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MISSION LAYER                           │
│              Behavior Tree Engine (py_trees)                │
│        [Takeoff → Search → Approach → Wait → Land]          │
├─────────────────────────────────────────────────────────────┤
│                    PLANNING LAYER                           │
│         Path Planning | Visual Servoing | Search            │
├─────────────────────────────────────────────────────────────┤
│                   WORLD MODEL LAYER                         │
│        State Estimator (Vehicle + Target Fusion)            │
├─────────────────────────────────────────────────────────────┤
│                   PERCEPTION LAYER                          │
│        Target Detector (ArUco | YOLO | Custom...)           │
├─────────────────────────────────────────────────────────────┤
│                    CONTROL LAYER                            │
│      Vehicle Controller | Safety Monitor | FSM              │
├─────────────────────────────────────────────────────────────┤
│             HARDWARE ABSTRACTION LAYER (HAL)                │
│              MAVROS Interface | Camera Interface            │
└─────────────────────────────────────────────────────────────┘
                           ↓
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌──────────┐            ┌──────────────┐
        │   SITL   │            │   Hardware   │
        │  Gazebo  │            │  RPi5 + FC   │
        └──────────┘            └──────────────┘
```

### Package Structure

```
src/
├── uav_msgs/              # Custom ROS2 interfaces (actions, msgs, srvs)
├── uav_control/           # Vehicle controller, FSM, safety monitor
├── uav_perception/        # Target detection (future)
├── uav_mission/           # Behavior tree executor (future)
└── uav_bringup/           # Launch files and configs (future)
```

---

## 🔑 Critical Design Decisions

### ArduPilot GUIDED Mode Behavior

**Key Insight**: ArduPilot uses a two-layer control model that differs from PX4:

```
┌────────────────────────────────────────────┐
│  FLIGHT PHASE CONTROL (Native Commands)   │
│  • NAV_TAKEOFF - Required to lift off      │
│  • NAV_LAND - Controlled descent           │
│  • After takeoff: GUIDED Loiter (auto)     │
└────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────┐
│  POSITION CONTROL (Setpoint Streaming)    │
│  • ONLY for active movement                │
│  • NOT required to maintain hover          │
│  • ArduPilot holds autonomously            │
└────────────────────────────────────────────┘
```

**Implications**:
- ✅ Must use `/mavros/cmd/takeoff` service (position setpoints alone won't work)
- ✅ After NAV_TAKEOFF, drone holds position without continuous setpoints
- ✅ Failsafe only triggers on GCS heartbeat loss (not setpoint loss)
- ✅ No "HoldPosition" action needed - ArduPilot does this natively

[→ Read the learning log](documents/learning-logs/2025-12-25-ardupilot-takeoff-land-fix.md)

### FSM vs Behavior Trees

**Design Decision**: Use both, each for specific purposes:

| Component | Use Case | Rationale |
|-----------|----------|-----------|
| **FSM** | Safety envelope (DISARMED→ARMED→FLYING) | Deterministic, verifiable, formal methods possible |
| **BT** | Mission logic (Search→Detect→Approach) | Composable, reactive, easy to modify |

**Principle**: FSM manages WHAT the vehicle CAN do. BT decides WHAT it SHOULD do.

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Make
- (Optional) ArduPilot SITL for testing

### Installation

```bash
# Clone the repository
git clone https://github.com/Shadow-Harvest/sh-uav-platform.git
cd sh-uav-platform

# Build Docker image (first time only)
make docker-build

# Enter development container
make dev
```

### Running Your First Flight (SITL)

**Terminal 1 - ArduPilot SITL:**
```bash
cd ~/ardupilot/ArduCopter
sim_vehicle.py -v ArduCopter --console --map --out=udp:0.0.0.0:14550
```

**Terminal 2 - ROS2 + MAVROS:**
```bash
make dev

# Inside container:
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch mavros apm.launch fcu_url:=udp://:14550@host.docker.internal:14550
```

**Terminal 3 - Test Flight:**
```bash
docker exec -it $(docker ps -q) bash

# Inside container:
source /opt/ros/humble/setup.bash
source install/setup.bash

# Execute takeoff action
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 5.0, timeout_sec: 30.0}"

# Watch it hover autonomously for a few seconds...

# Land
ros2 action send_goal /vehicle/land uav_msgs/action/Land \
  "{timeout_sec: 30.0}"
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make dev` | Enter development container shell |
| `make build` | Build ROS2 workspace |
| `make test` | Build and run all tests |
| `make clean` | Remove build artifacts |
| `make docker-build` | Rebuild Docker image from scratch |

---

## 💻 Development Guide

### Development Environment Architecture

```
Mac/Linux (host)                 Docker Container
────────────────────────────────────────────────────────
~/sh-uav-platform/
├── src/      ◄───mounted───►  /ws/src/      (live code)
├── build/    ◄───mounted───►  /ws/build/    (cache)
├── install/  ◄───mounted───►  /ws/install/  (binaries)
└── docker/                    ROS2 Humble + deps
```

**Hot-reload workflow**: Edit on host → Builds in container → No restart needed

### TDD Workflow

```bash
# Terminal 1: VS Code editing files on host

# Terminal 2: Fast iteration in container
make dev
source /opt/ros/humble/setup.bash
source install/setup.bash

# Fast test commands:
colcon build --packages-select uav_control          # Build one package
pytest src/uav_control/test/test_vehicle_controller.py  # Run one test file
pytest src/uav_control/test/test_vehicle_controller.py::test_takeoff  # One test
```

### Testing Strategy

```
        ┌─────────────┐
        │    SITL     │  ← Full mission tests
        │   Tests     │    (GitHub Actions)
        ├─────────────┤
        │Integration  │  ← Multi-node tests
        │   Tests     │    (launch_testing)
        ├─────────────┤
        │    Unit     │  ← Component logic
        │   Tests     │    (pytest, 80% coverage)
        └─────────────┘
```

**Run all tests:**
```bash
make test
```

### Code Style

- **Python**: Follow PEP 8, use `ruff` for linting
- **Docstrings**: Google style with Args/Returns/Raises
- **Type hints**: Required for all public functions
- **Comments**: Only where logic isn't self-evident

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-aruco-detector

# Make changes, test
make test

# Commit with descriptive message
git commit -m "Add ArUco detector with pose estimation

- Implement OpenCV ArUco detection
- Add camera intrinsics calibration
- Include unit tests with test images
- Update documentation"

# Push and create PR
git push origin feature/add-aruco-detector
```

---

## 📚 Documentation

### Learning Logs

Detailed session notes documenting the development journey:

- [2025-12-25: ArduPilot Takeoff/Land Fix](documents/learning-logs/2025-12-25-ardupilot-takeoff-land-fix.md) - Discovery of ArduPilot's autonomous hold behavior
- [2025-12-12: Takeoff Action Server](documents/learning-logs/2025-12-12-takeoff-action-server.md)
- [2025-12-10: Actions](documents/learning-logs/2025-12-10-actions.md)
- [2025-12-08: Vehicle FSM](documents/learning-logs/2025-12-08-vehicle-fsm.md)
- [More learning logs...](documents/learning-logs/)

### Additional Resources

- [📋 Project Roadmap](documents/roadmap.md) - Detailed implementation plan (16-week timeline)
- [🗂️ Archived Docs](documents/archive/) - Previous architecture documents

---

## 🗺️ Project Status & Roadmap

### Completed Milestones

- ✅ **Week 1-3: Foundation**
  - Docker SITL environment with ArduPilot + Gazebo
  - MAVROS integration and communication verified
  - Vehicle FSM with state transitions
  - Takeoff/Land actions using NAV_TAKEOFF/NAV_LAND
  - Discovered ArduPilot autonomous hold behavior

### Current Sprint

- 🚧 **Week 4-6: Perception**
  - Camera pipeline from Gazebo
  - ArUco marker detection
  - Pose estimation and TF broadcasting
  - Target tracking with smoothing

### Upcoming Work

1. **Mission Layer** (Weeks 7-9)
   - py_trees behavior tree framework
   - Search behaviors (rotate search)
   - Complete search & detect mission

2. **Visual Servoing** (Weeks 10-12)
   - Approach controller (PBVS)
   - Full mission: Takeoff → Search → Approach → Land

3. **Integration & CI** (Weeks 13-14)
   - Automated test suite
   - GitHub Actions CI/CD
   - Documentation polish

4. **Hardware Deployment** (Weeks 15-16)
   - Raspberry Pi 5 setup
   - Real camera integration
   - Outdoor flight testing

[→ View detailed roadmap](documents/roadmap.md)

---

## 🛠️ Hardware Setup

### SITL (Current)

- **OS**: Ubuntu 22.04 (Docker container)
- **Flight Controller**: ArduPilot SITL
- **Simulator**: Gazebo Harmonic
- **Computer**: Development machine (Mac/Linux/WSL2)

### Target Hardware (Phase 6)

- **Companion Computer**: Raspberry Pi 5 (8GB)
- **Flight Controller**: ArduPilot-compatible FC (Pixhawk, etc.)
- **Camera**: USB camera or RPi Camera Module
- **Frame**: Quadcopter frame (TBD)

### WSL2 GPU Setup (for Gazebo)

```bash
# Install NVIDIA Container Toolkit (one-time)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Enable X11 for GUI
sudo apt-get install -y x11-xserver-utils
xhost +local:docker
```

---

## 🤝 Contributing

This is a personal portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes with clear messages
4. Ensure tests pass (`make test`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ROS2 Community** - For excellent documentation and tools
- **ArduPilot Team** - For the robust autopilot software
- **py_trees** - For the behavior tree framework
- **MAVROS** - For ROS-MAVLink bridge

---

## 📞 Contact

**Andrey Negovskiy**
- GitHub: [@Shadow-Harvest](https://github.com/Shadow-Harvest)
- Email: a.negovskiy@gmail.com

---

**Built with ❤️ using ROS2, ArduPilot, and Test-Driven Development**
