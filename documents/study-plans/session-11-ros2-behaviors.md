# Session 11: ROS2 Behavior Wrappers

**Phase:** 3 - Mission Framework
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium-High

---

## Prerequisites

- [ ] Session 10 complete (py_trees understood)
- [ ] Actions working: Takeoff, Land, FlyToPosition, YawTo
- [ ] py_trees and py_trees_ros installed

---

## Learning Objectives

By the end of this session, you will understand:

1. **py_trees_ros integration** - ROS2 behaviors
2. **Action client behaviors** - wrapping ROS2 actions
3. **Topic subscriber behaviors** - condition checks from topics
4. **Blackboard ↔ ROS2** - sharing data

---

## Practical Objectives

### Primary Goal
Create uav_mission package with reusable behavior wrappers for existing actions.

### Deliverables

1. **Create `uav_mission` package:**
   ```bash
   ros2 pkg create uav_mission --build-type ament_python \
     --dependencies rclpy py_trees py_trees_ros uav_msgs
   ```

2. **Implement action behavior base class:**
   ```python
   class RosActionBehavior(py_trees.behaviour.Behaviour):
       """Base class for ROS2 action-based behaviors."""
   ```

3. **Wrap existing actions:**
   - `TakeoffBehavior` - wraps Takeoff action
   - `LandBehavior` - wraps Land action
   - `FlyToPositionBehavior` - wraps FlyToPosition action
   - `YawToBehavior` - wraps YawTo action

4. **Create condition behaviors:**
   - `IsTargetVisible` - checks /tracking/targets
   - `IsAtAltitude` - checks current altitude
   - `IsBatteryOk` - checks battery level (placeholder)

5. **Unit tests:**
   - Test behavior initialization
   - Test status mapping (action result → behavior status)

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Study py_trees_ros action client pattern |
| 0:30-1:15 | Implement RosActionBehavior base class |
| 1:15-1:45 | Implement TakeoffBehavior |
| 1:45-2:15 | Implement LandBehavior and FlyToPositionBehavior |
| 2:15-2:45 | Implement condition behaviors |
| 2:45-3:15 | Write unit tests |
| 3:15-3:45 | Test with simple tree in SITL |
| 3:45-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Package builds
colcon build --packages-select uav_mission

# 2. Simple test tree works
# Create test script that:
# - Creates Sequence(TakeoffBehavior, LandBehavior)
# - Ticks until complete
# - Verifies drone took off and landed

# 3. Conditions work
# Test IsTargetVisible returns SUCCESS when marker in view
```

---

## Key Questions to Answer During Session

1. How does action client feedback map to behavior RUNNING?
2. When should a behavior return FAILURE vs throw exception?
3. How to handle action timeout in behavior?
4. Should goal be sent in initialise() or update()?

---

## ROS2 Action Behavior Pattern

```python
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from rclpy.action import ActionClient

class RosActionBehavior(Behaviour):
    """Base class for ROS2 action behaviors."""

    def __init__(self, name, node, action_type, action_name):
        super().__init__(name)
        self.node = node
        self.action_client = ActionClient(node, action_type, action_name)
        self.goal_handle = None
        self.result = None

    def initialise(self):
        """Called when behavior becomes active. Send goal here."""
        self.goal_handle = None
        self.result = None

        # Wait for action server
        if not self.action_client.wait_for_server(timeout_sec=1.0):
            self.feedback_message = "Action server not available"
            return

        # Create and send goal (override in subclass)
        goal = self.create_goal()
        future = self.action_client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_callback)

    def update(self):
        """Check action status."""
        if self.result is not None:
            if self.result.success:
                return Status.SUCCESS
            else:
                self.feedback_message = self.result.message
                return Status.FAILURE

        if self.goal_handle is None:
            return Status.RUNNING

        if not self.goal_handle.accepted:
            return Status.FAILURE

        return Status.RUNNING

    def terminate(self, new_status):
        """Cancel action if behavior is interrupted."""
        if self.goal_handle is not None and new_status == Status.INVALID:
            self.goal_handle.cancel_goal_async()

    def create_goal(self):
        """Override to create action goal."""
        raise NotImplementedError
```

---

## Condition Behavior Pattern

```python
class IsTargetVisible(Behaviour):
    """Check if target is visible in tracking."""

    def __init__(self, name, node, target_id=None):
        super().__init__(name)
        self.node = node
        self.target_id = target_id  # None = any target
        self.last_tracks = None

        # Subscribe to tracking
        self.sub = node.create_subscription(
            TrackedTargetArray,
            '/tracking/targets',
            self._callback,
            10
        )

    def update(self):
        if self.last_tracks is None:
            return Status.FAILURE

        for track in self.last_tracks.targets:
            if self.target_id is None or track.detection.target_id == self.target_id:
                if track.time_since_last_seen_sec < 0.5:
                    return Status.SUCCESS

        return Status.FAILURE
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Action timeout | Behavior stuck RUNNING | Add timeout decorator |
| Node not spinning | Callbacks not received | Ensure executor running |
| Goal rejected | Immediate FAILURE | Check FSM state guards |
| Async confusion | Race conditions | Use callbacks properly |

---

## Code Locations

- Package: `src/uav_mission/`
- Behaviors: `src/uav_mission/uav_mission/behaviors/`
  - `__init__.py`
  - `actions.py` (TakeoffBehavior, LandBehavior, etc.)
  - `conditions.py` (IsTargetVisible, IsAtAltitude, etc.)
- Tests: `src/uav_mission/test/test_behaviors.py`

---

## Definition of Done

- [ ] uav_mission package created
- [ ] RosActionBehavior base class implemented
- [ ] TakeoffBehavior works
- [ ] LandBehavior works
- [ ] FlyToPositionBehavior works
- [ ] YawToBehavior works
- [ ] IsTargetVisible condition works
- [ ] At least 3 unit tests
- [ ] Simple Sequence(Takeoff, Land) works in SITL
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 12 will implement the RotateSearch behavior - a more complex behavior that rotates the drone in steps until a target is detected.
