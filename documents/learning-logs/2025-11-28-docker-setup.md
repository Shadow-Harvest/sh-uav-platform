# Learning Log: Docker Setup & First Flight

**Date:** 2025-11-28

## What Was Built
- Dockerized ROS2 Humble development environment
- Cross-platform setup supporting macOS and PC (WSL Ubuntu)
- Multi-file Docker Compose configuration with OS-specific overrides

## Key Technical Learnings

### Docker Compose Override Pattern
- `compose.yml`: Base configuration
- `compose.mac.yml`: Mac-specific overrides (bridge network, no GPU)
- `compose.gpu.yml`: PC overrides (NVIDIA GPU, X11 forwarding)
- Makefile detects OS and applies correct compose files automatically

### Volume Mounting Strategy
```
src/     -> /ws/src/      (live code editing)
build/   -> /ws/build/    (persistent build cache)
install/ -> /ws/install/  (built ROS2 packages)
```
Enables editing on host, building in container, with persistent caching.

### Platform-Specific Differences
- **Mac**: Uses `network_mode: bridge`, no GPU/GUI support
- **PC (WSL Ubuntu)**: Uses `network_mode: host`, NVIDIA GPU passthrough works
- Gazebo rendering confirmed working on PC with GPU

### MAVROS Drone Control
Successfully controlled drone using ROS2 commands through MAVROS:
- **Set mode to GUIDED**: Enables autonomous control
- **Arm**: Arms the drone motors
- **Takeoff**: Autonomous takeoff
- **Land**: Autonomous landing

Commands executed via ROS2 services interfacing with MAVROS.

## Verified Working
- Docker image builds on both Mac and PC
- Container starts and bash shell accessible via `make dev`
- Gazebo GUI launches successfully on PC with WSL Ubuntu
- Volume mounts functional for live development workflow
- Drone takeoff and landing via MAVROS commands

## Quick Commands
```bash
make docker-build    # Build image
make dev            # Enter container
make build          # Build ROS2 workspace
make sim            # Launch Gazebo (PC only)
```
