.PHONY: help dev build test pytest clean docker-build docker-clean

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

## Simulation (run these inside dev container - use 'make dev' first)
sim-help: ## Show simulation startup instructions
	@echo ""
	@echo "To run the simulation, you need 3 terminals:"
	@echo ""
	@echo "1. Start the dev container:"
	@echo "   make dev"
	@echo ""
	@echo "Inside the container, open 3 terminals and run:"
	@echo ""
	@echo "Terminal 1 - Gazebo:"
	@echo "   gz sim -v4 /opt/ardupilot_gazebo/worlds/iris_runway.sdf"
	@echo ""
	@echo "Terminal 2 - ArduPilot SITL (wait for Gazebo to load):"
	@echo "   cd /opt/ardupilot/ArduCopter && sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console"
	@echo ""
	@echo "Terminal 3 - MAVROS (wait for SITL to connect):"
	@echo "   ros2 launch mavros apm.launch fcu_url:=udp://:14550@localhost:14555"
	@echo ""
	@echo "Or use VS Code Dev Containers for integrated terminal experience."
	@echo ""
