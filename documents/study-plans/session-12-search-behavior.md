# Session 12: Search Behavior

**Phase:** 3 - Mission Framework
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 11 complete (behavior wrappers work)
- [ ] YawTo action working in SITL
- [ ] IsTargetVisible condition working

---

## Learning Objectives

By the end of this session, you will understand:

1. **Stateful behaviors** - maintaining state across ticks
2. **Iterative actions** - repeating with changing parameters
3. **Condition-based termination** - external success criteria
4. **Blackboard for state sharing**

---

## Practical Objectives

### Primary Goal
Implement RotateSearchBehavior that rotates the drone in steps until a target is detected.

### Deliverables

1. **Implement `RotateSearchBehavior`:**
   - Rotates drone by step_deg (e.g., 30°) on each cycle
   - Pauses at each heading to allow detection
   - Checks IsTargetVisible condition between rotations
   - Succeeds when target found
   - Fails after full 360° rotation with no detection

2. **Configure via parameters:**
   - `step_deg`: Rotation step size (default 30°)
   - `pause_sec`: Pause at each heading (default 2.0)
   - `max_rotations`: Number of full rotations (default 1)

3. **Integrate with Blackboard:**
   - Write detected target info to blackboard on success
   - Available for subsequent behaviors

4. **Unit tests:**
   - Test rotation sequence
   - Test early termination on detection
   - Test failure after full rotation

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Design behavior state machine |
| 0:30-1:15 | Implement basic rotation logic |
| 1:15-1:45 | Add detection checking |
| 1:45-2:15 | Add pause between rotations |
| 2:15-2:45 | Integrate blackboard output |
| 2:45-3:15 | Write unit tests |
| 3:15-3:45 | SITL testing |
| 3:45-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Unit tests pass
pytest src/uav_mission/test/test_search_behavior.py -v

# 2. SITL test: No marker visible
# Place marker behind drone, start search
# Drone should rotate until marker found

# 3. SITL test: Marker visible immediately
# Place marker in front, search should succeed quickly

# 4. SITL test: No marker anywhere
# Search should fail after 360° rotation
```

---

## Key Questions to Answer During Session

1. How to track current heading vs target heading?
2. When to transition from ROTATING → PAUSING → CHECKING?
3. How to handle YawTo timeout or failure?
4. Should detection check be synchronous or via blackboard?

---

## Behavior State Machine

```
           ┌─────────────┐
           │   INITIAL   │
           └──────┬──────┘
                  │ initialise()
                  ▼
           ┌─────────────┐
           │  ROTATING   │ ← YawTo action running
           └──────┬──────┘
                  │ yaw complete
                  ▼
           ┌─────────────┐
           │   PAUSING   │ ← Wait for detection
           └──────┬──────┘
                  │ pause complete
                  ▼
           ┌─────────────┐
    ┌──────│  CHECKING   │──────┐
    │      └─────────────┘      │
    │ target found              │ no target
    ▼                           ▼
┌───────────┐            ┌─────────────┐
│  SUCCESS  │            │ More steps? │
└───────────┘            └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │ yes                   │ no (360° done)
                    ▼                       ▼
             ┌─────────────┐         ┌───────────┐
             │  ROTATING   │         │  FAILURE  │
             └─────────────┘         └───────────┘
```

---

## Implementation Sketch

```python
class RotateSearchBehavior(Behaviour):
    """Rotate in steps until target detected."""

    class State(Enum):
        ROTATING = auto()
        PAUSING = auto()
        CHECKING = auto()

    def __init__(self, name, node, step_deg=30.0, pause_sec=2.0, max_rotations=1):
        super().__init__(name)
        self.node = node
        self.step_deg = step_deg
        self.pause_sec = pause_sec
        self.max_steps = int(360 / step_deg) * max_rotations

        self.yaw_behavior = YawToBehavior("rotate_yaw", node)
        self.is_target_visible = IsTargetVisible("check_target", node)

        self.state = None
        self.current_yaw = 0.0
        self.steps_completed = 0
        self.pause_start = None

    def initialise(self):
        self.state = self.State.ROTATING
        self.steps_completed = 0
        self.current_yaw = self._get_current_yaw()
        self._start_rotation()

    def update(self):
        if self.state == self.State.ROTATING:
            return self._handle_rotating()
        elif self.state == self.State.PAUSING:
            return self._handle_pausing()
        elif self.state == self.State.CHECKING:
            return self._handle_checking()

    def _handle_rotating(self):
        status = self.yaw_behavior.update()
        if status == Status.RUNNING:
            return Status.RUNNING
        elif status == Status.SUCCESS:
            self.state = self.State.PAUSING
            self.pause_start = time.time()
            return Status.RUNNING
        else:
            return Status.FAILURE  # Yaw failed

    def _handle_pausing(self):
        if time.time() - self.pause_start >= self.pause_sec:
            self.state = self.State.CHECKING
        return Status.RUNNING

    def _handle_checking(self):
        if self.is_target_visible.update() == Status.SUCCESS:
            self._write_target_to_blackboard()
            return Status.SUCCESS

        self.steps_completed += 1
        if self.steps_completed >= self.max_steps:
            return Status.FAILURE

        # Continue searching
        self.state = self.State.ROTATING
        self._start_rotation()
        return Status.RUNNING
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Yaw not completing | Stuck in ROTATING | Check YawTo tolerance |
| Detection missed | Rotates past target | Increase pause duration |
| State confusion | Unexpected transitions | Add logging, debug state |
| Heading wrap | Jumps at ±180° | Normalize angles properly |

---

## Code Locations

- Behavior: `src/uav_mission/uav_mission/behaviors/search.py`
- Tests: `src/uav_mission/test/test_search_behavior.py`

---

## Definition of Done

- [ ] RotateSearchBehavior implemented
- [ ] Rotates by configurable step size
- [ ] Pauses at each heading
- [ ] Succeeds when target detected
- [ ] Fails after full rotation(s)
- [ ] Writes target to blackboard on success
- [ ] At least 3 unit tests
- [ ] SITL: successfully finds marker behind drone
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 13 will implement the mission executor node that runs complete behavior trees.
