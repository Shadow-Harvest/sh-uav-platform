# Session 02: FlyToPosition Action

**Phase:** 1B - Control Layer Completion
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 01 complete (setpoint streaming works)
- [ ] Understand ROS2 action server pattern (review Takeoff implementation)
- [ ] SITL environment ready

---

## Learning Objectives

By the end of this session, you will understand:

1. **Position control via setpoints** - how drone follows target position
2. **Coordinate frames** - LOCAL_NED, body frame, map frame
3. **Goal completion criteria** - defining "arrived" with tolerance
4. **Velocity-based approach** (optional advanced topic)

---

## Practical Objectives

### Primary Goal
Implement FlyToPosition action that moves the drone to a target (x, y, z) position.

### Deliverables

1. **Create `FlyToPosition.action`** in `uav_msgs/action/`:
   ```
   # Goal
   float32 x
   float32 y
   float32 z
   float32 yaw_deg        # Target yaw (-180 to 180), NaN = maintain current
   float32 tolerance_m    # Arrival tolerance (default 0.3m)
   float32 timeout_sec
   ---
   # Result
   bool success
   string message
   float32 final_distance_m
   ---
   # Feedback
   float32 distance_remaining_m
   float32 time_elapsed_sec
   geometry_msgs/Point current_position
   ```

2. **Implement action server** in `vehicle_controller.py`:
   - `_execute_fly_to_position()` method
   - Set control_mode to MOVING
   - Update target_pose continuously
   - Monitor distance to target
   - Reset control_mode to IDLE on completion

3. **Unit tests:**
   - Test goal acceptance
   - Test distance calculation
   - Test tolerance-based completion
   - Test timeout handling

4. **SITL test:**
   - Takeoff to 3m
   - FlyToPosition (5, 5, 3)
   - Verify drone moves and arrives

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:20 | Design action interface, review similar implementations |
| 0:20-0:40 | Create and build FlyToPosition.action |
| 0:40-1:30 | Implement _execute_fly_to_position() |
| 1:30-2:00 | Implement distance calculation and completion logic |
| 2:00-2:30 | Write unit tests |
| 2:30-3:30 | SITL testing and debugging |
| 3:30-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Action interface generated
ros2 interface show uav_msgs/action/FlyToPosition

# 2. Unit tests pass
pytest src/uav_control/test/test_vehicle_controller.py -v -k "fly"

# 3. SITL test sequence
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"

ros2 action send_goal /vehicle/fly_to_position uav_msgs/action/FlyToPosition \
  "{x: 5.0, y: 5.0, z: 3.0, yaw_deg: 0.0, tolerance_m: 0.3, timeout_sec: 30.0}"
# Should see drone move and feedback with distance_remaining

# 4. Verify final position
ros2 topic echo /mavros/local_position/pose --once
# Should show x≈5, y≈5, z≈3
```

---

## Key Questions to Answer During Session

1. What coordinate frame is `/mavros/setpoint_position/local` in?
2. How do you calculate 3D distance between current and target pose?
3. What's a reasonable tolerance for "arrived"? (consider GPS noise, control lag)
4. Should yaw be controlled simultaneously or sequentially?

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Drone oscillates | Never reaches tolerance | Increase tolerance, check setpoint rate |
| Slow movement | Takes very long | Check setpoint target is updating |
| Wrong direction | Moves opposite | Frame mismatch, check ENU vs NED |
| Action rejected | Goal status = REJECTED | Check _is_move_allowed() |

---

## Code Locations

- Action definition: `src/uav_msgs/action/FlyToPosition.action`
- CMakeLists update: `src/uav_msgs/CMakeLists.txt`
- Implementation: `src/uav_control/uav_control/vehicle_controller.py`
- Tests: `src/uav_control/test/test_vehicle_controller.py`

---

## Design Decisions to Make

1. **Yaw handling:**
   - Option A: Ignore yaw (always face forward)
   - Option B: Face direction of travel
   - Option C: Separate yaw parameter
   - **Recommended:** Option C with NaN = maintain current

2. **Arrival detection:**
   - Option A: Distance only
   - Option B: Distance + velocity near zero
   - **Recommended:** Option A (simpler, ArduPilot handles settling)

3. **What if already at target?**
   - Succeed immediately with distance_remaining = 0

---

## Definition of Done

- [ ] FlyToPosition.action created and builds
- [ ] Action server implemented
- [ ] Distance calculation tested
- [ ] Tolerance completion works
- [ ] Timeout handling works
- [ ] At least 3 new unit tests
- [ ] SITL test: takeoff → fly to (5,5,3) → verify position
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 03 will add YawTo action for rotation control. This is essential for the search behavior where the drone needs to rotate to scan for targets.
