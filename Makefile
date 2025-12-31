.PHONY: help dev build test pytest clean docker-build docker-clean sim-help sitl mavros

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

## Simulation - Docker SITL (for CI and headless testing)
sitl: ## Start ArduPilot SITL in Docker (headless)
	@echo "Starting SITL in Docker..."
	@/ws/scripts/start_sitl.sh

sitl-gazebo: ## Start ArduPilot SITL connected to native Gazebo
	@echo "Starting SITL with Gazebo backend..."
	@/ws/scripts/start_sitl.sh --gazebo

mavros: ## Start MAVROS (connects to SITL on localhost)
	@source /opt/ros/humble/setup.bash && \
	ros2 launch mavros apm.launch fcu_url:=udp://:14551@127.0.0.1:14550

## Simulation Help
sim-help: ## Show simulation startup instructions
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════════╗"
	@echo "║                    SIMULATION SETUP OPTIONS                           ║"
	@echo "╚═══════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo "  OPTION A: Full Docker (CI/Headless) - No Gazebo visualization"
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Terminal 1 (Docker):"
	@echo "    make dev"
	@echo "    /ws/scripts/start_sitl.sh    # or: make sitl"
	@echo ""
	@echo "  Terminal 2 (Docker - new shell):"
	@echo "    docker exec -it \$$(docker ps -qf ancestor=sh_uav_platform-dev) bash"
	@echo "    source /opt/ros/humble/setup.bash"
	@echo "    ros2 launch mavros apm.launch fcu_url:=udp://:14551@127.0.0.1:14550"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo "  OPTION B: Hybrid (Mac Dev) - Native Gazebo + Native SITL + Docker ROS2"
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Terminal 1 (Mac native - Gazebo server):"
	@echo "    gz-server -r iris_runway.sdf"
	@echo ""
	@echo "  Terminal 2 (Mac native - Gazebo GUI):"
	@echo "    gz-gui"
	@echo ""
	@echo "  Terminal 3 (Mac native - SITL):"
	@echo "    sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON \\"
	@echo "      --console --map --out=udp:0.0.0.0:14550"
	@echo ""
	@echo "  Terminal 4 (Docker - MAVROS):"
	@echo "    make dev"
	@echo "    source /opt/ros/humble/setup.bash"
	@echo "    ros2 launch mavros apm.launch fcu_url:=udp://:14550@host.docker.internal:14550"
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo "  OPTION C: Hybrid (Mac Dev) - Native Gazebo + Docker SITL + Docker ROS2"
	@echo "═══════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "  Terminal 1 (Mac native - Gazebo server):"
	@echo "    gz-server -r iris_runway.sdf"
	@echo ""
	@echo "  Terminal 2 (Mac native - Gazebo GUI):"
	@echo "    gz-gui"
	@echo ""
	@echo "  Terminal 3 (Docker - SITL):"
	@echo "    make dev"
	@echo "    /ws/scripts/start_sitl.sh --gazebo"
	@echo ""
	@echo "  Terminal 4 (Docker - MAVROS):"
	@echo "    docker exec -it \$$(docker ps -qf ancestor=sh_uav_platform-dev) bash"
	@echo "    source /opt/ros/humble/setup.bash"
	@echo "    ros2 launch mavros apm.launch fcu_url:=udp://:14551@127.0.0.1:14550"
	@echo ""
	@echo "TROUBLESHOOTING:"
	@echo "  - SITL not starting: check /tmp/arducopter.log and /tmp/mavproxy.log"
	@echo "  - MAVROS can't connect: verify port numbers match (14550/14551)"
	@echo "  - Gazebo not found: export GZ_SIM_RESOURCE_PATH=~/path/to/worlds"
	@echo ""
