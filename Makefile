.PHONY: build test dev sim clean help

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

docker-build: ## Build Docker image
	docker compose $(COMPOSE_FILES) build

clean: ## Clean build artifacts
	rm -rf build/ install/ log/

docker-clean: ## Remove Docker image
	docker compose $(COMPOSE_FILES) down --rmi local