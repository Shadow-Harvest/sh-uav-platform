# Session 18: Testing Infrastructure

**Phase:** 5 - Integration & Polish
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Phase 4 complete (full mission works)
- [ ] All packages building
- [ ] Basic pytest knowledge

---

## Learning Objectives

By the end of this session, you will understand:

1. **Test pyramid** - unit, integration, system tests
2. **ROS2 testing patterns** - launch_testing, mocking
3. **Test fixtures** - setup, teardown, parameterization
4. **Coverage measurement** - identifying gaps

---

## Practical Objectives

### Primary Goal
Create comprehensive test suite with unit, integration, and documented SITL tests.

### Deliverables

1. **Audit existing tests:**
   - List all current tests
   - Identify coverage gaps
   - Prioritize missing tests

2. **Add missing unit tests:**
   - Target: 80%+ line coverage for core modules
   - Focus on: FSM, controller, detector, tracker

3. **Create integration tests:**
   - Multi-node tests with launch_testing
   - Control → MAVROS mock
   - Perception → detection pipeline

4. **Document SITL test procedures:**
   - Manual test scripts
   - Expected outcomes
   - Failure criteria

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Audit existing tests, measure coverage |
| 0:30-1:15 | Write missing unit tests (prioritized) |
| 1:15-2:00 | Create launch_testing integration test |
| 2:00-2:30 | Measure and improve coverage |
| 2:30-3:15 | Document SITL test procedures |
| 3:15-3:45 | Run full test suite, fix failures |
| 3:45-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Run all unit tests
colcon test
colcon test-result --verbose

# 2. Measure coverage
pytest src/uav_control/test/ --cov=src/uav_control/uav_control --cov-report=html
# Open htmlcov/index.html

# 3. Run integration tests
ros2 launch uav_control test_controller_integration.launch.py

# 4. All tests pass
# 0 failures
```

---

## Key Questions to Answer During Session

1. What's more valuable - more unit tests or integration tests?
2. How to mock MAVROS for testing?
3. How to test behaviors without full tree?
4. What coverage percentage is "good enough"?

---

## Test Audit Template

| Package | Module | Current Tests | Coverage | Priority Tests Needed |
|---------|--------|---------------|----------|----------------------|
| uav_control | vehicle_fsm | 8 | 95% | ✓ Good |
| uav_control | vehicle_controller | 5 | 60% | Error handling, timeout |
| uav_control | vehicle_state_node | 2 | 40% | State transitions |
| uav_perception | aruco_detector | 2 | 50% | Edge cases, no detection |
| uav_perception | target_tracker | 3 | 55% | Timeout, multiple targets |
| uav_mission | behaviors | 4 | 45% | All behaviors |
| uav_mission | missions | 1 | 30% | Mission completion |

---

## Integration Test with launch_testing

```python
# test/test_controller_integration.py
import pytest
import rclpy
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_testing.actions import ReadyToTest
import launch_testing.markers

@pytest.mark.launch_test
@launch_testing.markers.keep_alive
def generate_test_description():
    return LaunchDescription([
        Node(
            package='uav_control',
            executable='vehicle_controller',
            name='vehicle_controller',
        ),
        ReadyToTest(),
    ])

class TestControllerIntegration:
    def test_takeoff_action_available(self, launch_service, proc_info, proc_output):
        """Verify takeoff action server starts."""
        # Use action client to check availability
        ...

    def test_lifecycle_transitions(self, ...):
        """Verify lifecycle state machine works."""
        ...
```

---

## MAVROS Mock for Testing

```python
class MockMAVROS:
    """Mock MAVROS services for unit testing."""

    def __init__(self, node):
        # Create mock services
        self.arm_srv = node.create_service(
            CommandBool,
            '/mavros/cmd/arming',
            self._arm_callback
        )
        self.mode_srv = node.create_service(
            SetMode,
            '/mavros/set_mode',
            self._mode_callback
        )

        self.armed = False
        self.mode = "STABILIZE"

    def _arm_callback(self, request, response):
        self.armed = request.value
        response.success = True
        return response

    def _mode_callback(self, request, response):
        self.mode = request.custom_mode
        response.mode_sent = True
        return response
```

---

## SITL Test Procedure Document

```markdown
## SITL Test: Full Search-Approach Mission

### Setup
1. Start Gazebo: `make gazebo`
2. Start SITL: `make sitl`
3. Wait for GPS lock (green HOME in console)
4. Start MAVROS: `make mavros`
5. Start control: `ros2 run uav_control vehicle_controller`
6. Configure lifecycle: `ros2 lifecycle set ...`

### Test Steps
1. Launch mission: `ros2 launch uav_mission search_approach.launch.py`
2. Observe:
   - [ ] Takeoff to 5m
   - [ ] Rotation search begins
   - [ ] Marker detected (visible in /tracking/targets)
   - [ ] Approach toward marker
   - [ ] Descent to 1.5m
   - [ ] Hover for 10s
   - [ ] Land complete

### Pass Criteria
- All phases complete
- Final position within 0.5m of marker XY
- Final altitude 0 (landed)
- No crashes or exceptions

### Failure Modes
- Search timeout: marker not visible, check camera
- Approach failure: detection lost, check tracker
- Land rejected: FSM state wrong, check state node
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Mock not intercepting | Real service called | Check topic/service names |
| launch_testing fails | Test hangs | Check node startup |
| Coverage tool missing | Command not found | pip install pytest-cov |
| Flaky tests | Pass/fail randomly | Add waits, improve synchronization |

---

## Code Locations

- Unit tests: `src/*/test/test_*.py`
- Integration tests: `src/*/test/integration/`
- SITL docs: `documents/testing/sitl-procedures.md`

---

## Definition of Done

- [ ] Test audit completed
- [ ] At least 5 new unit tests added
- [ ] At least 1 integration test created
- [ ] Coverage > 70% for core modules
- [ ] All tests pass
- [ ] SITL test procedures documented
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 19 will set up CI/CD with GitHub Actions for automated testing.
