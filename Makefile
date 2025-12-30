.PHONY: help dev build test pytest clean docker-build docker-clean sim-help

# Detect OS for correct compose file
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
    COMPOSE_FILES := -f docker/compose.yml -f docker/compose.mac.yml
else
    COMPOSE_FILES := -f docker/compose.yml -f docker/compose.gpu.yml
endif

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

## Development
dev: ## Enter development container shell
	docker compose $(COMPOSE_FILES) run --rm dev bash

build: ## Build ROS2 workspace
	docker compose $(COMPOSE_FILES) run --rm dev bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

## Testing
test: ## Run all ROS2 tests
	docker compose $(COMPOSE_FILES) run --rm dev bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install && colcon test && colcon test-result --verbose"

pytest: ## Run pytest only (fast TDD)
	docker compose $(COMPOSE_FILES) run --rm dev bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install --packages-select uav_control && source install/setup.bash && pytest src/uav_control/test/ -v"

## Docker Management
docker-build: ## Build Docker image
	docker compose $(COMPOSE_FILES) build

docker-clean: ## Remove Docker image and containers
	docker compose $(COMPOSE_FILES) down --rmi local

clean: ## Clean build artifacts
	rm -rf build/ install/ log/

## Simulation (Hybrid Setup: Native Gazebo + Docker SITL)
sim-help: ## Show simulation startup instructions
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════╗"
	@echo "║           HYBRID SIMULATION SETUP (Mac + Docker)                  ║"
	@echo "╠══════════════════════════════════════════════════════════════════╣"
	@echo "║  Gazebo runs NATIVELY on Mac (Metal GPU)                         ║"
	@echo "║  SITL + MAVROS + ROS2 run in Docker                              ║"
	@echo "╚══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "STEP 1: Start Gazebo on Mac (2 terminals)"
	@echo "────────────────────────────────────────────"
	@echo "  Terminal 1 (server):"
	@echo "    gz-server ~/Robotics/ardupilot_gazebo/worlds/iris_runway.sdf"
	@echo ""
	@echo "  Terminal 2 (GUI):"
	@echo "    gz-gui"
	@echo ""
	@echo "STEP 2: Start Docker container"
	@echo "────────────────────────────────────────────"
	@echo "  Terminal 3:"
	@echo "    make dev"
	@echo ""
	@echo "STEP 3: Inside Docker, start SITL"
	@echo "────────────────────────────────────────────"
	@echo "  (in Docker shell):"
	@echo "    sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON \\"
	@echo "      --sim-address host.docker.internal --console"
	@echo ""
	@echo "STEP 4: Inside Docker, start MAVROS (new terminal)"
	@echo "────────────────────────────────────────────"
	@echo "  docker exec -it sh_uav_platform-dev bash"
	@echo "  source /opt/ros/humble/setup.bash && source /ws/install/setup.bash"
	@echo "  ros2 launch mavros apm.launch fcu_url:=udp://:14550@localhost:14555"
	@echo ""
	@echo "NOTE: If Gazebo aliases don't work, run: source ~/.zshrc"
	@echo ""
