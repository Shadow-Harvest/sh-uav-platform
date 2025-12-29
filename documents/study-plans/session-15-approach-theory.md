# Session 15: Approach Controller Theory

**Phase:** 4 - Visual Servoing
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium-High (conceptual)

---

## Prerequisites

- [ ] Phase 3 complete (search mission works)
- [ ] Target tracker providing world-frame poses
- [ ] Basic control theory helpful but not required

---

## Learning Objectives

By the end of this session, you will understand:

1. **Visual servoing types** - IBVS, PBVS, hybrid
2. **Position-based visual servoing** - using 3D pose
3. **Control loop design** - P/PD/PID for approach
4. **Safety constraints** - velocity limits, approach angle

---

## Practical Objectives

### Primary Goal
Design the approach controller on paper, understand tradeoffs, prepare for implementation.

### Deliverables

1. **Study PBVS approach:**
   - Understand pose error calculation
   - Design control law
   - Identify key parameters

2. **Design approach strategy:**
   - Horizontal centering over target
   - Altitude descent profile
   - Final approach and hover

3. **Identify safety requirements:**
   - Maximum velocity limits
   - Minimum altitude for abort
   - Detection loss handling

4. **Document design** in learning log

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:45 | Read about PBVS, study examples |
| 0:45-1:15 | Design control law on paper |
| 1:15-1:45 | Plan approach phases |
| 1:45-2:15 | Define safety constraints |
| 2:15-2:45 | Write pseudo-code for controller |
| 2:45-3:00 | Document design decisions |

---

## Key Concepts

### Position-Based Visual Servoing (PBVS)

```
Camera → Detector → 3D Pose → Transform to World → Control Error → Velocity Command
                         ↑
                    TF (camera → map)
```

**Why PBVS for this project:**
- Simple: 3D pose directly gives position error
- ArUco provides good 3D estimates
- Works well at medium distances (1-10m)

### Control Law (Proportional)

```
Position error:
  e_x = target.x - drone.x
  e_y = target.y - drone.y
  e_z = target.z - desired_altitude_above_target - drone.z

Velocity command (P-controller):
  v_x = Kp * e_x
  v_y = Kp * e_y
  v_z = Kp * e_z

With saturation:
  v_x = clamp(v_x, -v_max, v_max)
  ...
```

### Approach Phases

```
Phase 1: CENTERING
- Fly horizontally to be above target
- Maintain current altitude
- Transition when |e_xy| < threshold

Phase 2: DESCENDING
- Descend while maintaining XY centering
- Use slower Kp for Z
- Transition when altitude < final_altitude

Phase 3: FINAL_APPROACH
- Fine centering at low altitude
- Very slow movements
- Transition when |e_xyz| < final_threshold

Phase 4: HOVER
- Hold position
- Mission complete
```

---

## Key Questions to Answer During Session

1. What Kp value gives stable, responsive behavior?
2. How to handle temporary detection loss during approach?
3. Should descent rate be constant or proportional to error?
4. What's the minimum altitude to maintain for safety?
5. When is "close enough" to declare success?

---

## Safety Constraints Table

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| v_max_horizontal | 1.0 m/s | Safe for indoor/close work |
| v_max_vertical | 0.5 m/s | Slower descent for safety |
| min_altitude | 1.0 m | Ground clearance |
| detection_timeout | 2.0 s | Abort if lost too long |
| final_distance | 0.3 m | Close enough for "arrived" |

---

## Pseudo-code Design

```python
class ApproachController:
    def __init__(self):
        self.Kp_xy = 0.5      # Horizontal gain
        self.Kp_z = 0.3       # Vertical gain (slower)
        self.v_max_xy = 1.0   # m/s
        self.v_max_z = 0.5    # m/s
        self.phase = CENTERING
        self.last_detection_time = None

    def compute_velocity(self, target_pose, drone_pose, desired_hover_alt):
        # Check detection freshness
        if self._detection_stale():
            return HOLD_COMMAND

        # Compute error
        e_x = target_pose.x - drone_pose.x
        e_y = target_pose.y - drone_pose.y
        e_z = target_pose.z + desired_hover_alt - drone_pose.z

        # Phase-specific logic
        if self.phase == CENTERING:
            # Only XY control, maintain altitude
            v_x = self._clamp(self.Kp_xy * e_x, self.v_max_xy)
            v_y = self._clamp(self.Kp_xy * e_y, self.v_max_xy)
            v_z = 0.0

            if self._xy_centered(e_x, e_y):
                self.phase = DESCENDING

        elif self.phase == DESCENDING:
            # XY + Z control
            v_x = self._clamp(self.Kp_xy * e_x, self.v_max_xy)
            v_y = self._clamp(self.Kp_xy * e_y, self.v_max_xy)
            v_z = self._clamp(self.Kp_z * e_z, self.v_max_z)

            if drone_pose.z <= desired_hover_alt + 0.5:
                self.phase = FINAL_APPROACH

        # ... more phases

        return VelocityCommand(v_x, v_y, v_z)
```

---

## Verification (Conceptual)

- [ ] Control law makes sense physically
- [ ] Phases cover full approach sequence
- [ ] Safety constraints are reasonable
- [ ] Edge cases considered (detection loss, oscillation)
- [ ] Pseudo-code ready for implementation

---

## Definition of Done

- [ ] Understand PBVS approach
- [ ] Control law designed with gains
- [ ] Approach phases defined
- [ ] Safety constraints documented
- [ ] Pseudo-code written
- [ ] Learning log updated
- [ ] Ready for implementation

---

## Notes for Next Session

Session 16 will implement the approach controller as a ROS2 node and behavior.
