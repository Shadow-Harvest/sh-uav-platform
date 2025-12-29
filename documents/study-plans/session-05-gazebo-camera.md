# Session 05: Gazebo Camera Setup

**Phase:** 2 - Perception Pipeline
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium-High (Gazebo/URDF work can be tricky)

---

## Prerequisites

- [ ] Phase 1B complete (all control actions work)
- [ ] SITL + Gazebo environment running
- [ ] Basic understanding of URDF/SDF models
- [ ] Familiarity with TF2 (transform frames)

---

## Learning Objectives

By the end of this session, you will understand:

1. **Gazebo sensor plugins** - how cameras are simulated
2. **Camera intrinsics** - focal length, principal point, distortion
3. **Coordinate frames** - camera_link vs camera_optical_frame
4. **TF tree** - base_link → camera transforms

---

## Practical Objectives

### Primary Goal
Add a downward-facing camera to the drone model in Gazebo with correct TF.

### Deliverables

1. **Modify drone model (SDF/URDF):**
   - Add camera link with proper offset from base_link
   - Add camera sensor with gazebo_ros_camera plugin
   - Configure reasonable parameters (640x480, 30Hz)

2. **Verify topics published:**
   - `/camera/image_raw` - raw image
   - `/camera/camera_info` - intrinsic parameters
   - `/camera/image_raw/compressed` (if using compressed transport)

3. **Configure TF:**
   - Ensure `camera_link` → `camera_optical_frame` transform exists
   - Verify with `ros2 run tf2_tools view_frames`

4. **Visual verification:**
   - View camera feed in rqt_image_view
   - Verify ground is visible when hovering

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Research Gazebo camera plugins, find example models |
| 0:30-1:00 | Locate drone model file, understand structure |
| 1:00-1:45 | Add camera sensor to model |
| 1:45-2:15 | Configure camera parameters and TF |
| 2:15-2:45 | Test in Gazebo, debug issues |
| 2:45-3:15 | Verify TF tree and image topics |
| 3:15-3:30 | Commit, document |

---

## Verification Checklist

```bash
# 1. Topics exist
ros2 topic list | grep camera
# Should see: /camera/image_raw, /camera/camera_info

# 2. Image publishing at expected rate
ros2 topic hz /camera/image_raw
# Expected: ~30 Hz

# 3. View image
ros2 run rqt_image_view rqt_image_view
# Select /camera/image_raw, should see Gazebo world from drone's perspective

# 4. Check TF tree
ros2 run tf2_tools view_frames
# Should show: base_link → camera_link → camera_optical_frame

# 5. Camera info has valid intrinsics
ros2 topic echo /camera/camera_info --once
# K matrix should be non-zero
```

---

## Key Questions to Answer During Session

1. What's the difference between `camera_link` and `camera_optical_frame`?
2. Why do we need camera_info for ArUco detection?
3. How does camera pose affect what's visible during hover?
4. What resolution/FPS tradeoff is appropriate for detection?

---

## Camera Configuration Reference

**Reasonable starting parameters:**
```xml
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>  <!-- 60 degrees -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <plugin name="camera_plugin" filename="libgazebo_ros_camera.so">
    <ros>
      <namespace></namespace>
      <remapping>image_raw:=camera/image_raw</remapping>
      <remapping>camera_info:=camera/camera_info</remapping>
    </ros>
    <camera_name>camera</camera_name>
    <frame_name>camera_optical_frame</frame_name>
  </plugin>
</sensor>
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Camera not appearing | No topics | Check plugin path, sensor type |
| Black image | Image all zeros | Check camera clip distances |
| Wrong orientation | Image upside down | Adjust camera_link orientation |
| No TF | Transform not found | Check frame_name in plugin |
| Low FPS | <10 Hz | Reduce resolution, check CPU |

---

## Code/File Locations

- Drone model: `~/ardupilot_gazebo/models/iris_with_ardupilot/` (or similar)
- World file: `~/ardupilot_gazebo/worlds/iris_arducopter_runway.world`
- New camera config: Consider creating custom model in project

---

## TF Frame Conventions

```
base_link (drone body, X forward)
    │
    └── camera_link (physical camera mount)
            │
            └── camera_optical_frame (Z forward, X right, Y down)
                                      ↑ Required for image processing
```

**Why camera_optical_frame?**
- OpenCV/image processing uses Z-forward convention
- ROS/robotics uses X-forward convention
- camera_optical_frame bridges these conventions

---

## Definition of Done

- [ ] Camera sensor added to drone model
- [ ] /camera/image_raw publishes at 30Hz
- [ ] /camera/camera_info has valid intrinsics
- [ ] TF: base_link → camera_link → camera_optical_frame
- [ ] Image viewable in rqt_image_view
- [ ] Ground visible when drone hovers at 3m
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 06 will add an ArUco marker to the Gazebo world at a known location. This gives you something for the camera to detect.
