# Session 16: Approach Implementation

**Phase:** 4 - Visual Servoing
**Estimated Duration:** 4-5 hours
**Difficulty:** High

---

## Prerequisites

- [ ] Session 15 complete (approach design done)
- [ ] FlyToPosition action working (uses setpoint streaming)
- [ ] Target tracker providing world-frame poses
- [ ] Control design pseudo-code ready

---

## Learning Objectives

By the end of this session, you will understand:

1. **Velocity setpoint control** - different from position setpoints
2. **Real-time control loops** - maintaining update rate
3. **Sensor fusion** - combining pose estimates with commands
4. **Graceful degradation** - handling sensor dropout

---

## Practical Objectives

### Primary Goal
Implement ApproachBehavior that uses visual servoing to approach and hover over target.

### Deliverables

1. **Create `ApproachAction` definition:**
   ```
   # Goal
   string target_id           # Target to approach
   float32 hover_altitude_m   # Final altitude above target
   float32 timeout_sec
   ---
   # Result
   bool success
   string message
   float32 final_distance_m
   ---
   # Feedback
   float32 distance_to_target_m
   string phase               # CENTERING, DESCENDING, FINAL, HOVER
   float32 time_elapsed_sec
   ```

2. **Implement approach controller:**
   - P-controller for position error
   - Phase state machine
   - Velocity command output
   - Safety limits

3. **Implement ApproachBehavior:**
   - Wraps approach action
   - Uses blackboard for target pose
   - Reports progress

4. **Unit tests:**
   - Test phase transitions
   - Test velocity saturation
   - Test detection loss handling

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Create ApproachAction, build msgs |
| 0:30-1:30 | Implement ApproachController class |
| 1:30-2:30 | Implement action server in vehicle_controller |
| 2:30-3:00 | Implement ApproachBehavior |
| 3:00-3:30 | Write unit tests |
| 3:30-4:30 | SITL testing and tuning |
| 4:30-5:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Action defined
ros2 interface show uav_msgs/action/Approach

# 2. Unit tests pass
pytest src/uav_control/test/test_approach_controller.py -v

# 3. SITL test
# Place marker at (3, 3, 0)
# Takeoff to 5m at (0, 0, 5)
ros2 action send_goal /vehicle/approach uav_msgs/action/Approach \
  "{target_id: 'aruco_42', hover_altitude_m: 1.5, timeout_sec: 60.0}"

# Drone should:
# 1. Fly horizontally toward (3, 3, 5)
# 2. Descend while centering to (3, 3, 1.5)
# 3. Fine-tune and hover

# 4. Verify final position
ros2 topic echo /mavros/local_position/pose --once
# Should be approximately (3, 3, 1.5)
```

---

## Key Questions to Answer During Session

1. How to switch from position setpoints to velocity setpoints?
2. How often should control loop run? (10-20 Hz)
3. What to do if target moves during approach?
4. How to smoothly transition between phases?

---

## Velocity Command via MAVROS

```python
from geometry_msgs.msg import TwistStamped

# Publisher for velocity setpoints
self.vel_pub = self.create_publisher(
    TwistStamped,
    '/mavros/setpoint_velocity/cmd_vel',
    10
)

def publish_velocity(self, vx, vy, vz):
    msg = TwistStamped()
    msg.header.stamp = self.get_clock().now().to_msg()
    msg.header.frame_id = 'base_link'  # or 'map' depending on config
    msg.twist.linear.x = vx
    msg.twist.linear.y = vy
    msg.twist.linear.z = vz
    self.vel_pub.publish(msg)
```

---

## Approach Controller Implementation

```python
class ApproachController:
    """P-controller for target approach."""

    class Phase(Enum):
        CENTERING = auto()
        DESCENDING = auto()
        FINAL_APPROACH = auto()
        HOVER = auto()
        LOST = auto()

    def __init__(self):
        # Gains
        self.Kp_xy = 0.5
        self.Kp_z = 0.3

        # Limits
        self.v_max_xy = 1.0
        self.v_max_z = 0.5

        # Thresholds
        self.centering_threshold = 0.5  # meters
        self.final_altitude_offset = 0.5  # meters above target alt
        self.arrival_threshold = 0.3  # meters

        # State
        self.phase = self.Phase.CENTERING
        self.last_target_time = None
        self.detection_timeout = 2.0

    def update(self, target_pose, drone_pose, hover_alt):
        """Compute velocity command."""

        # Check for detection loss
        if self._is_detection_stale():
            self.phase = self.Phase.LOST
            return (0.0, 0.0, 0.0), False  # Hold, not complete

        # Update last detection time
        self.last_target_time = time.time()

        # Compute errors
        e_x = target_pose.x - drone_pose.x
        e_y = target_pose.y - drone_pose.y
        target_hover_z = target_pose.z + hover_alt
        e_z = target_hover_z - drone_pose.z

        distance_xy = math.sqrt(e_x**2 + e_y**2)
        distance_total = math.sqrt(e_x**2 + e_y**2 + e_z**2)

        # Phase-specific control
        if self.phase == self.Phase.CENTERING:
            vx = self._clamp(self.Kp_xy * e_x, self.v_max_xy)
            vy = self._clamp(self.Kp_xy * e_y, self.v_max_xy)
            vz = 0.0  # Maintain altitude

            if distance_xy < self.centering_threshold:
                self.phase = self.Phase.DESCENDING

        elif self.phase == self.Phase.DESCENDING:
            vx = self._clamp(self.Kp_xy * e_x, self.v_max_xy)
            vy = self._clamp(self.Kp_xy * e_y, self.v_max_xy)
            vz = self._clamp(self.Kp_z * e_z, self.v_max_z)

            if abs(e_z) < self.final_altitude_offset:
                self.phase = self.Phase.FINAL_APPROACH

        elif self.phase == self.Phase.FINAL_APPROACH:
            # Slower gains for precision
            vx = self._clamp(0.3 * e_x, 0.3)
            vy = self._clamp(0.3 * e_y, 0.3)
            vz = self._clamp(0.2 * e_z, 0.2)

            if distance_total < self.arrival_threshold:
                self.phase = self.Phase.HOVER

        elif self.phase == self.Phase.HOVER:
            # Zero velocity, mission complete
            return (0.0, 0.0, 0.0), True

        return (vx, vy, vz), False

    def _clamp(self, value, limit):
        return max(-limit, min(limit, value))

    def _is_detection_stale(self):
        if self.last_target_time is None:
            return True
        return time.time() - self.last_target_time > self.detection_timeout
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Drone oscillates | Bounces around target | Reduce Kp gains |
| Never reaches target | Slow or stuck | Increase Kp or check threshold |
| Phase stuck | Won't transition | Debug phase logic |
| Velocity not applied | Drone doesn't move | Check velocity topic, QoS |
| Detection drops | Approach aborts | Increase timeout, check tracker |

---

## Code Locations

- Action: `src/uav_msgs/action/Approach.action`
- Controller: `src/uav_control/uav_control/approach_controller.py`
- Action server: Add to `vehicle_controller.py`
- Behavior: `src/uav_mission/uav_mission/behaviors/approach.py`
- Tests: `src/uav_control/test/test_approach_controller.py`

---

## Tuning Parameters

| Parameter | Default | Tune Range | Effect |
|-----------|---------|------------|--------|
| Kp_xy | 0.5 | 0.2 - 1.0 | Horizontal responsiveness |
| Kp_z | 0.3 | 0.1 - 0.5 | Vertical responsiveness |
| v_max_xy | 1.0 | 0.5 - 2.0 | Max horizontal speed |
| v_max_z | 0.5 | 0.2 - 1.0 | Max vertical speed |
| centering_threshold | 0.5 | 0.3 - 1.0 | When to start descent |
| arrival_threshold | 0.3 | 0.1 - 0.5 | "Close enough" |

---

## Definition of Done

- [ ] Approach.action created and builds
- [ ] ApproachController class implemented
- [ ] Action server in vehicle_controller
- [ ] ApproachBehavior wraps action
- [ ] Phase transitions work correctly
- [ ] Safety limits enforced
- [ ] At least 3 unit tests
- [ ] SITL: Successfully approaches marker
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 17 will integrate the approach into a full mission: Search → Approach → Hover → Land
