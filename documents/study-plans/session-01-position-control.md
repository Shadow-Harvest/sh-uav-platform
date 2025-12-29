# Session 01: Position Control Activation

**Phase:** 1B - Control Layer Completion
**Estimated Duration:** 1.5-2 hours
**Difficulty:** Low (mostly uncommenting + understanding)

---

## Prerequisites

- [ ] SITL environment verified working
- [ ] `make build` succeeds
- [ ] Existing tests pass: `make test`
- [ ] Read `documents/2025-12-29-project-review-and-replan.md`

---

## Learning Objectives

By the end of this session, you will understand:

1. **Why setpoint streaming was disabled** and when it's needed
2. **The difference between GUIDED Loiter and active position control**
3. **Control modes concept** - when to stream vs when to let ArduPilot hold
4. **Timer-based publishing** in ROS2 lifecycle nodes

---

## Practical Objectives

### Primary Goal
Enable 20Hz setpoint streaming with a control mode that determines when to publish.

### Deliverables

1. **Modify `vehicle_controller.py`:**
   - Add `control_mode` attribute: `'IDLE'`, `'HOLDING'`, `'MOVING'`
   - Uncomment setpoint timer in `on_activate()`
   - Modify `_publish_setpoint()` to only publish when mode is `'MOVING'`
   - Add `set_control_mode()` method

2. **Add unit tests:**
   - Test that setpoints NOT published when mode is `'IDLE'`
   - Test that setpoints ARE published when mode is `'MOVING'`
   - Test timer frequency (verify 20Hz)

3. **Manual SITL verification:**
   - Activate node, set mode to MOVING
   - Verify `/mavros/setpoint_position/local` publishes at 20Hz

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:15 | Review current code, understand why streaming was commented |
| 0:15-0:30 | Design control mode state machine (on paper) |
| 0:30-1:00 | Implement control mode and modify setpoint publishing |
| 1:00-1:20 | Write unit tests |
| 1:20-1:40 | SITL verification |
| 1:40-2:00 | Commit, document learnings |

---

## Verification Checklist

```bash
# 1. Build succeeds
make build

# 2. Unit tests pass
pytest src/uav_control/test/test_vehicle_controller.py -v

# 3. In SITL: verify setpoints publish at 20Hz when mode is MOVING
ros2 topic hz /mavros/setpoint_position/local
# Expected: average rate: 20.xxx

# 4. Verify NO setpoints when mode is IDLE
# (check node logs or topic hz shows 0)
```

---

## Key Questions to Answer During Session

1. Why does ArduPilot need continuous setpoints for movement but not for hovering?
2. What happens if setpoint streaming stops mid-flight during active movement?
3. When should control_mode transition between states?

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Timer not firing | No setpoints published | Check lifecycle state is ACTIVE |
| QoS mismatch | MAVROS doesn't receive | Verify BEST_EFFORT QoS |
| Executor issues | Callbacks delayed | Use MultiThreadedExecutor |

---

## Code Locations

- Primary file: `src/uav_control/uav_control/vehicle_controller.py`
- Test file: `src/uav_control/test/test_vehicle_controller.py`
- Commented code: lines 105-118

---

## Definition of Done

- [ ] Control mode enum/state added
- [ ] Setpoint timer uncommented and working
- [ ] Setpoints only publish in MOVING mode
- [ ] At least 2 new unit tests
- [ ] SITL verification recorded (screenshot or log)
- [ ] Committed with descriptive message

---

## Notes for Next Session

After this session, you'll have the infrastructure for position control but no way to USE it yet. Session 02 will implement FlyToPosition action which actually moves the drone.
