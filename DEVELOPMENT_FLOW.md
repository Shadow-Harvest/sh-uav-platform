# Development Flow - UAV Control Platform

## Project Context
ArduPilot ROS2 UAV control system with OpenCV ArUco marker tracking. 
Development split between MacBook (unit testing) and PC (integration testing with hardware).

## Architecture: Clean Architecture + SOLID

### Layer Structure
```
Domain Layer (Pure Python - No ROS dependencies)
├── entities/        # Data models (UAV state, position, markers)
├── use_cases/       # Business logic (TakeoffUseCase, TrackMarkerUseCase)
└── interfaces/      # Abstract interfaces (IFlightController, IVisionSystem)

Application Layer (ROS adapters)
├── nodes/           # ROS node implementations
└── converters/      # ROS message converters

Infrastructure Layer (Platform-specific)
├── mavros_controller.py    # Real hardware implementation
├── opencv_vision.py        # Computer vision implementation
└── mock_controller.py      # Testing implementation
```

### SOLID Principles Application
- **S**: One use case = one responsibility
- **O**: Extend via new use cases, don't modify existing
- **L**: Mock implementations must behave like real ones
- **I**: Small focused interfaces (IFlightController, IVisionSystem)
- **D**: Use cases depend on abstractions, not concrete classes

## Project Structure
```
src/uav_control/
├── uav_control/
│   ├── domain/                    # Pure Python - Unit testable
│   │   ├── entities/
│   │   ├── use_cases/
│   │   └── interfaces/
│   ├── application/               # ROS-dependent
│   │   ├── nodes/
│   │   └── converters/
│   └── infrastructure/            # Platform-specific implementations
│
├── test/
│   ├── unit/                      # MacBook-friendly, fast
│   └── integration/               # PC-only, requires ROS/MAVROS
│
├── setup.py
├── package.xml
├── pytest.ini
└── requirements-dev.txt
```

## Development Environments

### MacBook (Fast TDD Loop)
**Purpose:** Unit test domain logic without ROS installation

**Requirements:**
- Python 3.10+
- Virtual environment with: pytest, pytest-cov, pytest-mock, numpy, opencv-python
- Message type stubs (lightweight dataclasses)

**What to avoid:**
- Full ROS 2 installation
- MAVROS/MAVLink
- ArduPilot SITL

### PC (Integration Validation)
**Purpose:** Integration testing with real ROS/MAVROS/SITL

**Requirements:**
- Full ROS 2 Humble
- MAVROS
- ArduPilot SITL
- All MacBook requirements

## TDD Workflow

### MacBook Development (Red-Green-Refactor)
```bash
# 1. Write failing test
# test/unit/domain/test_takeoff_use_case.py

# 2. Run tests
pytest -m unit -v --cov=uav_control/domain

# 3. Implement minimal code to pass
# uav_control/domain/use_cases/takeoff_use_case.py

# 4. Refactor and verify
pytest -m unit --cov

# 5. Commit when green
git commit -m "feat: implement takeoff use case"
```

### PC Integration Testing
```bash
# 1. Pull latest code
git pull

# 2. Verify unit tests still pass
pytest -m unit

# 3. Build ROS workspace
colcon build

# 4. Run integration tests
pytest -m integration

# 5. Manual testing with SITL
ros2 run uav_control control_node
```

## Code Example Pattern

### Domain Layer (MacBook testable)
```python
# domain/interfaces/flight_controller.py
from abc import ABC, abstractmethod

class IFlightController(ABC):
    @abstractmethod
    def set_position(self, position: Position) -> None:
        pass

    @abstractmethod
    def arm(self) -> bool:
        pass

# domain/use_cases/takeoff_use_case.py
class TakeoffUseCase:
    def __init__(self, controller: IFlightController):
        self._controller = controller

    def execute(self, altitude: float) -> bool:
        if altitude < 0 or altitude > 100:
            raise ValueError("Invalid altitude")

        position = Position(x=0, y=0, z=altitude)
        self._controller.set_position(position)
        return self._controller.arm()
```

### Unit Test (MacBook)
```python
# test/unit/domain/test_takeoff_use_case.py
from unittest.mock import Mock
import pytest

def test_takeoff_sets_correct_altitude():
    # Arrange
    mock_controller = Mock()
    use_case = TakeoffUseCase(mock_controller)

    # Act
    use_case.execute(altitude=2.5)

    # Assert
    mock_controller.set_position.assert_called_once()
    called_position = mock_controller.set_position.call_args[0][0]
    assert called_position.z == 2.5
```

### Infrastructure (PC testable)
```python
# infrastructure/mavros_controller.py
class MavrosFlightController(IFlightController):
    def __init__(self, node: Node):
        self._node = node
        self._setpoint_pub = node.create_publisher(
            PoseStamped, '/mavros/setpoint_position/local', 10
        )

    def set_position(self, position: Position) -> None:
        msg = PoseStamped()
        msg.pose.position.x = position.x
        msg.pose.position.y = position.y
        msg.pose.position.z = position.z
        self._setpoint_pub.publish(msg)
```

## Testing Configuration

### pytest.ini
```ini
[pytest]
testpaths = test
python_files = test_*.py
markers =
    unit: Unit tests (MacBook-friendly)
    integration: Integration tests (requires ROS/MAVROS)
    slow: Slow running tests
```

### Test Commands
```bash
# MacBook: Unit tests only
pytest -m unit

# PC: Integration tests only
pytest -m integration

# PC: All tests
pytest

# With coverage
pytest -m unit --cov=uav_control/domain --cov-report=html
```

## Git Workflow

```
MacBook:
├── Feature branch: git checkout -b feature/marker-tracking
├── TDD loop (unit tests)
├── Commit frequently
└── Push: git push origin feature/marker-tracking

↓

PC:
├── Pull: git pull origin feature/marker-tracking
├── Verify unit tests
├── Build: colcon build
├── Run integration tests
├── Manual SITL testing
└── Merge when validated
```

## Decision Matrix

| Task | Device | Test Type | Requires ROS |
|------|--------|-----------|--------------|
| Implement use case logic | MacBook | Unit | No |
| Test business rules | MacBook | Unit | No |
| Develop OpenCV algorithms | MacBook | Unit | No |
| Test ROS message handling | PC | Integration | Yes |
| Test MAVROS communication | PC | Integration | Yes |
| Test with SITL | PC | Manual | Yes |
| Full system validation | PC | End-to-end | Yes |

## Key Principles

1. **Domain logic is pure Python** - No ROS imports in domain layer
2. **Inject dependencies** - Use cases receive interfaces via constructor
3. **Mock at boundaries** - Mock IFlightController, not ROS directly
4. **Fast feedback** - Unit tests run in <1s
5. **Test behavior, not implementation** - Test what, not how
6. **Integration tests validate adapters** - Ensure infrastructure works with real systems

## Starting a New Feature

When requesting implementation in new conversation:

1. Specify the feature (e.g., "Implement ArUco marker tracking use case")
2. Reference this document: "Follow DEVELOPMENT_FLOW.md architecture"
3. Clarify development target:
   - "TDD on MacBook" = domain + unit tests
   - "Full implementation" = domain + infrastructure + integration tests
4. State dependencies (e.g., "Needs IVisionSystem interface")

## Quick Reference

**MacBook workflow:**
```bash
pytest -m unit --cov=uav_control/domain
```

**PC workflow:**
```bash
colcon build && pytest -m integration
```

**Add new use case:**
1. Create interface in `domain/interfaces/`
2. Create use case in `domain/use_cases/`
3. Write unit tests in `test/unit/domain/`
4. Create infrastructure implementation in `infrastructure/`
5. Write integration tests in `test/integration/`
