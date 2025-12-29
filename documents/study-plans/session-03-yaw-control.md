# Session 03: Yaw Control

**Phase:** 1B - Control Layer Completion
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 02 complete (FlyToPosition works)
- [ ] Understand quaternion basics (or willingness to learn)
- [ ] SITL environment ready

---

## Learning Objectives

By the end of this session, you will understand:

1. **Yaw representation** - degrees, radians, quaternions
2. **Yaw in setpoints** - how MAVROS expects orientation
3. **Yaw wrapping** - handling -180 to 180 boundary
4. **Rotation direction** - shortest path vs specified direction

---

## Practical Objectives

### Primary Goal
Implement YawTo action that rotates the drone to a specified heading.

### Deliverables

1. **Create `YawTo.action`** in `uav_msgs/action/`:
   ```
   # Goal
   float32 target_yaw_deg     # Target heading (-180 to 180, 0 = North/X+)
   float32 yaw_rate_deg_s     # Max rotation rate (0 = default 30 deg/s)
   float32 tolerance_deg      # Arrival tolerance (default 5 deg)
   float32 timeout_sec
   ---
   # Result
   bool success
   string message
   float32 final_yaw_deg
   ---
   # Feedback
   float32 current_yaw_deg
   float32 yaw_error_deg
   float32 time_elapsed_sec
   ```

2. **Implement helper functions:**
   - `quaternion_to_yaw(q)` - extract yaw from quaternion
   - `yaw_to_quaternion(yaw_deg)` - create quaternion from yaw
   - `normalize_angle(angle)` - wrap to -180 to 180
   - `angle_difference(a, b)` - shortest angular difference

3. **Implement action server:**
   - `_execute_yaw_to()` method
   - Modify setpoint orientation (not position)
   - Monitor yaw progress
   - Handle wrap-around correctly

4. **Unit tests:**
   - Test quaternion conversion (both directions)
   - Test angle normalization
   - Test angle difference (especially around ±180)

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Research: quaternions, MAVROS orientation, yaw conventions |
| 0:30-0:50 | Create and build YawTo.action |
| 0:50-1:20 | Implement helper functions with tests |
| 1:20-2:00 | Implement _execute_yaw_to() |
| 2:00-2:30 | SITL testing |
| 2:30-3:00 | Debug, commit, document |

---

## Verification Checklist

```bash
# 1. Action interface generated
ros2 interface show uav_msgs/action/YawTo

# 2. Helper function tests pass
pytest src/uav_control/test/test_vehicle_controller.py -v -k "yaw"

# 3. SITL test sequence
# Takeoff
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"

# Rotate to 90 degrees (East)
ros2 action send_goal /vehicle/yaw_to uav_msgs/action/YawTo \
  "{target_yaw_deg: 90.0, yaw_rate_deg_s: 30.0, tolerance_deg: 5.0, timeout_sec: 30.0}"

# Rotate to -90 degrees (West) - should go through 0, not 180
ros2 action send_goal /vehicle/yaw_to uav_msgs/action/YawTo \
  "{target_yaw_deg: -90.0, yaw_rate_deg_s: 30.0, tolerance_deg: 5.0, timeout_sec: 30.0}"

# 4. Verify yaw in Gazebo visually matches command
```

---

## Key Questions to Answer During Session

1. How does MAVROS/ArduPilot interpret yaw in setpoints?
2. What's the relationship between yaw and quaternion (w, x, y, z)?
3. How do you ensure the drone takes the shortest rotation path?
4. What happens to yaw during FlyToPosition if not specified?

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Yaw flips unexpectedly | Jumps 180° | Check quaternion sign conventions |
| Rotates wrong direction | Goes long way | Check angle_difference implementation |
| Yaw drifts | Doesn't hold target | Ensure continuous setpoint publishing |
| Quaternion errors | Invalid orientation | Verify normalization |

---

## Code Locations

- Action definition: `src/uav_msgs/action/YawTo.action`
- Implementation: `src/uav_control/uav_control/vehicle_controller.py`
- Consider: New utility module `src/uav_control/uav_control/math_utils.py`

---

## Reference: Quaternion for Pure Yaw

For rotation around Z-axis (yaw only, no roll/pitch):
```python
import math

def yaw_to_quaternion(yaw_rad):
    """Convert yaw angle to quaternion (assuming roll=pitch=0)."""
    return Quaternion(
        w=math.cos(yaw_rad / 2),
        x=0.0,
        y=0.0,
        z=math.sin(yaw_rad / 2)
    )

def quaternion_to_yaw(q):
    """Extract yaw from quaternion."""
    # atan2(2*(w*z + x*y), 1 - 2*(y² + z²))
    siny_cosp = 2 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)
```

---

## Definition of Done

- [ ] YawTo.action created and builds
- [ ] Quaternion ↔ yaw helpers implemented and tested
- [ ] Angle normalization and difference helpers tested
- [ ] Action server works in SITL
- [ ] Rotation takes shortest path
- [ ] At least 4 new unit tests
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 04 will integrate the FSM with the controller to ensure operations are only allowed in appropriate states. This is the final Phase 1B session before moving to perception.
