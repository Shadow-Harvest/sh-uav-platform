.PHONY: build test dev sim clean help
SHELL := /bin/bash

# Detect OS for correct compose file
UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
    COMPOSE_FILES := -f docker/compose.yml -f docker/compose.mac.yml
else
    COMPOSE_FILES := -f docker/compose.yml -f docker/compose.gpu.yml
endif

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Enter dev container shell
	docker compose $(COMPOSE_FILES) run --rm dev bash

build: ## Build ROS2 workspace
	docker compose $(COMPOSE_FILES) run --rm dev bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

test: ## Run all tests
	docker compose $(COMPOSE_FILES) run --rm dev bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install && colcon test && colcon test-result --verbose"

sim: ## Launch SITL simulation (PC only)
ifeq ($(UNAME), Darwin)
	@echo "Simulation with GUI not supported on Mac. Use 'make dev' and run headless tests."
else
	xhost +local:docker
	docker compose $(COMPOSE_FILES) up
endif

gazebo: ## Start Gazebo with drone model (Terminal 1)
	source /usr/share/gazebo/setup.bash && \
	export GAZEBO_MODEL_PATH=$$HOME/ardupilot_gazebo/models:$$GAZEBO_MODEL_PATH && \
	export GAZEBO_RESOURCE_PATH=$$HOME/ardupilot_gazebo/worlds:$$GAZEBO_RESOURCE_PATH && \
	cd ~/ardupilot_gazebo && \
	gazebo --verbose worlds/iris_arducopter_runway.world

sitl: ## Start ArduPilot SITL (Terminal 2 - after Gazebo is running)
	source /usr/share/gazebo/setup.bash && \
	export GAZEBO_MODEL_PATH=$$HOME/ardupilot_gazebo/models:$$GAZEBO_MODEL_PATH && \
	export GAZEBO_RESOURCE_PATH=$$HOME/ardupilot_gazebo/worlds:$$GAZEBO_RESOURCE_PATH && \
	cd ~/ardupilot/ArduCopter && \
	sim_vehicle.py -v ArduCopter -f gazebo-iris --console --map --out=udp:0.0.0.0:14550

mavros: ## Start MAVROS (Terminal 3 - run after SITL is up)
	docker compose $(COMPOSE_FILES) up -d && \
	sleep 3 && \
	docker exec -it sh_uav_platform-dev bash -c "source /opt/ros/humble/setup.bash && ros2 launch mavros apm.launch fcu_url:=udp://:14550@host.docker.internal:14550"

validate: ## Run Week 1 validation script (Terminal 4 - run after MAVROS connected)
	docker exec -it sh_uav_platform-dev bash -c "source /opt/ros/humble/setup.bash && cd /ws/scripts && python3 week1_validation.py"

docker-build: ## Build Docker image
	docker compose $(COMPOSE_FILES) build

clean: ## Clean build artifacts
	rm -rf build/ install/ log/

docker-clean: ## Remove Docker image
	docker compose $(COMPOSE_FILES) down --rmi local