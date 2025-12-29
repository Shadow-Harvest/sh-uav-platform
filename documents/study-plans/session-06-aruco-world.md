# Session 06: ArUco Marker World

**Phase:** 2 - Perception Pipeline
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 05 complete (camera working in Gazebo)
- [ ] Understand what ArUco markers are
- [ ] Image visible in rqt_image_view

---

## Learning Objectives

By the end of this session, you will understand:

1. **ArUco marker basics** - dictionary, ID, size, encoding
2. **Gazebo model creation** - SDF structure for visual models
3. **World file modification** - adding models to simulation
4. **Detection prerequisites** - marker visibility requirements

---

## Practical Objectives

### Primary Goal
Create an ArUco marker model and place it in the Gazebo world at a known position.

### Deliverables

1. **Generate ArUco marker image:**
   - Use OpenCV or online generator
   - Dictionary: DICT_4X4_50 (simple, robust)
   - ID: 42
   - Size: 0.15m (15cm) - visible from 2-5m altitude

2. **Create Gazebo marker model:**
   - SDF model with visual mesh/texture
   - Correct physical size (0.15m x 0.15m)
   - Flat on ground (no collision needed)

3. **Add marker to world:**
   - Position: (3.0, 3.0, 0.01) - slightly above ground
   - Orientation: facing up (marker visible from above)
   - Known position for testing

4. **Visual verification:**
   - Marker visible in Gazebo
   - Marker appears in camera when drone hovers overhead

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Research ArUco dictionaries, generate marker image |
| 0:30-1:00 | Create Gazebo model (SDF + texture) |
| 1:00-1:30 | Add model to world file |
| 1:30-2:00 | Test visibility in Gazebo and camera |
| 2:00-2:30 | Create multiple markers at different positions (optional) |
| 2:30-3:00 | Document marker positions, commit |

---

## Verification Checklist

```bash
# 1. Marker visible in Gazebo 3D view
# Look at ground in Gazebo, should see ArUco pattern

# 2. Marker visible in camera
# Hover drone over marker position (3, 3, 3)
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"
ros2 action send_goal /vehicle/fly_to_position uav_msgs/action/FlyToPosition \
  "{x: 3.0, y: 3.0, z: 3.0, yaw_deg: 0.0, tolerance_m: 0.3, timeout_sec: 30.0}"

# 3. View in rqt_image_view - should see marker in frame
ros2 run rqt_image_view rqt_image_view

# 4. Save reference screenshot for detector testing
```

---

## Key Questions to Answer During Session

1. Why DICT_4X4_50 instead of larger dictionaries?
2. How does marker size affect detection distance?
3. What's the minimum pixel size for reliable detection (~10-20px per cell)?
4. How does lighting in Gazebo affect detection?

---

## ArUco Marker Generation

**Using Python/OpenCV:**
```python
import cv2
import numpy as np

# Generate marker
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
marker_id = 42
marker_size = 200  # pixels

marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
cv2.imwrite('aruco_42.png', marker_image)
```

**Online generators:**
- https://chev.me/arucogen/ (select 4x4, ID 42)
- Save as PNG for Gazebo texture

---

## Gazebo Model Structure

```
aruco_marker_42/
├── model.config
├── model.sdf
└── materials/
    └── textures/
        └── aruco_42.png
```

**model.sdf:**
```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <model name="aruco_marker_42">
    <static>true</static>
    <link name="link">
      <visual name="visual">
        <geometry>
          <box>
            <size>0.15 0.15 0.001</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>model://aruco_marker_42/materials</uri>
            <name>ArUco/Marker42</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Marker not visible | Not in Gazebo | Check model path, world include |
| Texture not loading | White square | Check texture path, material script |
| Marker too small | Can't see in camera | Increase size or lower altitude |
| Marker washed out | Too bright/dark | Adjust Gazebo lighting |
| Z-fighting | Flickering | Raise marker slightly (z=0.01) |

---

## Code/File Locations

- Marker model: Create in `gazebo/models/aruco_marker_42/`
- World file: `~/ardupilot_gazebo/worlds/iris_arducopter_runway.world`
- Generated image: `aruco_42.png`

---

## Marker Positions for Testing

| Marker ID | Position (x, y, z) | Purpose |
|-----------|-------------------|---------|
| 42 | (3.0, 3.0, 0.01) | Primary test marker |
| 17 | (6.0, 6.0, 0.01) | Secondary (optional) |
| 23 | (-3.0, 3.0, 0.01) | Edge case testing |

Document these positions - you'll need them to verify detector accuracy.

---

## Definition of Done

- [ ] ArUco marker image generated (ID 42, DICT_4X4_50)
- [ ] Gazebo model created with correct size (0.15m)
- [ ] Model added to world at (3, 3, 0.01)
- [ ] Marker visible in Gazebo
- [ ] Marker appears in camera when drone hovers overhead
- [ ] Screenshot saved for detector testing
- [ ] Marker positions documented
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 07 will implement the ArUco detector node. You'll use OpenCV's aruco module to detect the marker and estimate its pose.
