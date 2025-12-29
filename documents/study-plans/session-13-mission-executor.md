# Session 13: Mission Executor

**Phase:** 3 - Mission Framework
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Sessions 10-12 complete
- [ ] All behaviors working individually
- [ ] Understand py_trees tree ticking

---

## Learning Objectives

By the end of this session, you will understand:

1. **Tree execution** - tick rates, threading considerations
2. **Mission lifecycle** - setup, execution, teardown
3. **Visualization** - py_trees viewer for debugging
4. **Error handling** - tree-level failure handling

---

## Practical Objectives

### Primary Goal
Create MissionExecutor node that runs behavior trees and provides mission status.

### Deliverables

1. **Implement `MissionExecutor` node:**
   - Load/create behavior tree
   - Tick tree at configurable rate (10Hz)
   - Publish mission status (MissionStatus message)
   - Handle tree completion (SUCCESS/FAILURE)

2. **Tree management:**
   - setup_with_descendants() on tree
   - tick_once() in timer callback
   - Proper cleanup on shutdown

3. **Status publishing:**
   - Current tree status
   - Active behavior name
   - Progress information (if available)

4. **Service interface (optional):**
   - /mission/start - start mission
   - /mission/abort - abort current mission
   - /mission/status - get status

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Design executor architecture |
| 0:30-1:15 | Implement basic MissionExecutor |
| 1:15-1:45 | Add status publishing |
| 1:45-2:15 | Test with simple tree |
| 2:15-2:45 | Add visualization support (py_trees viewer) |
| 2:45-3:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Executor starts
ros2 run uav_mission mission_executor

# 2. Status published
ros2 topic echo /mission/status

# 3. Simple mission runs
# Executor with Sequence(Takeoff, Land)
# Should see mission complete successfully

# 4. py_trees viewer works (optional)
py-trees-tree-watcher
```

---

## Key Questions to Answer During Session

1. What tick rate is appropriate for the behavior tree?
2. How to handle node shutdown during active mission?
3. Should tree be parameter-configured or code-defined?
4. How to report detailed progress from nested behaviors?

---

## Implementation Sketch

```python
class MissionExecutor(Node):
    """Executes behavior tree missions."""

    def __init__(self):
        super().__init__('mission_executor')

        # Parameters
        self.declare_parameter('tick_rate', 10.0)
        self.tick_rate = self.get_parameter('tick_rate').value

        # Mission state
        self.tree = None
        self.mission_active = False

        # Publishers
        self.status_pub = self.create_publisher(MissionStatus, '/mission/status', 10)

        # Timer for ticking
        self.tick_timer = None

    def start_mission(self, tree):
        """Start executing a behavior tree."""
        self.tree = tree
        self.tree.setup_with_descendants()
        self.mission_active = True

        # Start tick timer
        period = 1.0 / self.tick_rate
        self.tick_timer = self.create_timer(period, self._tick_callback)

        self.get_logger().info('Mission started')

    def _tick_callback(self):
        """Tick the tree and check for completion."""
        if not self.mission_active:
            return

        self.tree.tick_once()
        self._publish_status()

        # Check for completion
        if self.tree.status in [Status.SUCCESS, Status.FAILURE]:
            self._complete_mission()

    def _complete_mission(self):
        """Handle mission completion."""
        self.mission_active = False
        if self.tick_timer:
            self.tick_timer.cancel()

        result = "SUCCESS" if self.tree.status == Status.SUCCESS else "FAILURE"
        self.get_logger().info(f'Mission completed: {result}')

    def _publish_status(self):
        """Publish current mission status."""
        msg = MissionStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.mission_id = "current"
        msg.current_phase = str(self.tree.status)
        msg.current_behavior_node = self._get_active_behavior_name()
        self.status_pub.publish(msg)

    def _get_active_behavior_name(self):
        """Find currently running behavior."""
        # Traverse tree to find RUNNING node
        # ...
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Tree not ticking | No progress | Check timer running |
| Callbacks blocked | Tree hangs | Ensure behaviors non-blocking |
| Shutdown crash | Error on Ctrl+C | Proper cleanup in destructor |
| Status not updating | Stale data | Check publish in tick |

---

## Code Locations

- Executor: `src/uav_mission/uav_mission/mission_executor.py`
- Entry point: Add to setup.py
- Tests: `src/uav_mission/test/test_mission_executor.py`

---

## Definition of Done

- [ ] MissionExecutor node implemented
- [ ] Ticks tree at configurable rate
- [ ] Publishes MissionStatus
- [ ] Handles SUCCESS/FAILURE completion
- [ ] Simple mission runs end-to-end
- [ ] At least 2 unit tests
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 14 will assemble the complete search mission and run it end-to-end in SITL.
