# Session 09: Perception Integration

**Phase:** 2 - Perception Pipeline
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium
**PHASE GATE:** This session completes Phase 2

---

## Prerequisites

- [ ] Sessions 05-08 complete
- [ ] Camera, detector, tracker all working individually
- [ ] SITL environment ready

---

## Learning Objectives

By the end of this session, you will understand:

1. **Transform integration** - camera frame to world frame
2. **Launch file composition** - starting multiple nodes
3. **End-to-end validation** - verifying full pipeline
4. **Integration testing patterns**

---

## Practical Objectives

### Primary Goal
Integrate perception pipeline, add TF transforms, create launch file, and validate end-to-end.

### Deliverables

1. **Add TF integration to tracker:**
   - Transform poses from camera_optical_frame to map frame
   - Use tf2_ros for lookup
   - Handle transform exceptions gracefully

2. **Create perception launch file:**
   - Launch aruco_detector and target_tracker together
   - Configure parameters via launch file
   - Add remapping if needed

3. **Create integration test:**
   - Start perception nodes
   - Fly drone over marker
   - Verify tracked target pose matches known marker position

4. **End-to-end validation:**
   - Full pipeline: camera → detector → tracker → world-frame pose
   - Verify pose accuracy (within 0.2m of known marker position)

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Research tf2_ros, plan transform integration |
| 0:30-1:15 | Add TF lookup to tracker |
| 1:15-1:45 | Create perception launch file |
| 1:45-2:30 | Write integration test |
| 2:30-3:15 | SITL end-to-end validation |
| 3:15-3:45 | Debug and fix issues |
| 3:45-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Launch perception stack
ros2 launch uav_perception perception.launch.py

# 2. Verify nodes running
ros2 node list
# Should show: /aruco_detector, /target_tracker

# 3. Full test sequence
# Terminal 1: Start SITL (Gazebo + ArduPilot + MAVROS)
# Terminal 2: Launch perception
# Terminal 3: Launch control
# Terminal 4: Execute test

ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"
ros2 action send_goal /vehicle/fly_to_position uav_msgs/action/FlyToPosition \
  "{x: 3.0, y: 3.0, z: 3.0, tolerance_m: 0.3, timeout_sec: 30.0}"

# Check tracked target
ros2 topic echo /tracking/targets --once
# Pose should show position near (3, 3, 0) in map frame

# 4. Verify accuracy
# Known marker position: (3, 3, 0)
# Tracked position should be within 0.2m
```

---

## Key Questions to Answer During Session

1. What's the transform chain: camera_optical_frame → base_link → map?
2. How to handle "transform not available yet" on startup?
3. Should transform happen in tracker or detector?
4. How does drone movement affect detection accuracy?

---

## TF Transform Integration

```python
import tf2_ros
from tf2_geometry_msgs import do_transform_pose_stamped

class TargetTracker(Node):
    def __init__(self):
        # ... existing init ...

        # TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

    def transform_to_map(self, pose_stamped):
        """Transform pose from camera_optical_frame to map."""
        try:
            transform = self.tf_buffer.lookup_transform(
                'map',
                pose_stamped.header.frame_id,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.1)
            )
            return do_transform_pose_stamped(pose_stamped, transform)
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                tf2_ros.ExtrapolationException) as e:
            self.get_logger().warn(f'Transform failed: {e}')
            return None
```

---

## Launch File Structure

```python
# src/uav_perception/launch/perception.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='uav_perception',
            executable='aruco_detector',
            name='aruco_detector',
            parameters=[{
                'marker_size': 0.15,
                'dictionary': 'DICT_4X4_50'
            }]
        ),
        Node(
            package='uav_perception',
            executable='target_tracker',
            name='target_tracker',
            parameters=[{
                'smoothing_alpha': 0.3,
                'timeout_sec': 1.0
            }]
        ),
    ])
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Transform not found | Exception on lookup | Wait for TF to be available, add retry |
| Wrong frame result | Pose in camera frame | Check target_frame is 'map' |
| Pose jumps | Position not smooth after TF | Apply smoothing after transform |
| Old transforms | Extrapolation error | Use Time() for latest |
| Launch fails | Node not found | Check setup.py entry points |

---

## Code Locations

- Tracker with TF: `src/uav_perception/uav_perception/target_tracker.py`
- Launch file: `src/uav_perception/launch/perception.launch.py`
- Integration test: `src/uav_perception/test/test_perception_integration.py`

---

## Accuracy Validation

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Position error | < 0.2m | Compare tracked vs known (3,3,0) |
| Latency | < 200ms | Timestamp comparison |
| Detection rate | > 80% | Count detections / expected |
| Track stability | No drops | Monitor track_id consistency |

---

## Definition of Done

- [ ] TF transform integration working
- [ ] Tracked poses in map frame
- [ ] Perception launch file created
- [ ] All perception nodes start together
- [ ] Integration test passes
- [ ] End-to-end SITL validation:
  - [ ] Takeoff to 3m
  - [ ] Fly to (3, 3, 3)
  - [ ] Track shows marker at (3, 3, 0) ± 0.2m
- [ ] Committed with descriptive message

---

## Phase 2 Gate Criteria

Before proceeding to Phase 3, verify:

- [ ] Camera publishes images in SITL
- [ ] ArUco markers detected reliably
- [ ] Tracker produces smooth world-frame poses
- [ ] Pose error < 0.2m at 3m altitude
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] Document lessons learned

**Congratulations!** Phase 2 complete. You now have a working perception pipeline.

---

## Notes for Next Session

Phase 3 begins with Session 10: py_trees Fundamentals. You'll learn behavior tree concepts before implementing mission logic.
