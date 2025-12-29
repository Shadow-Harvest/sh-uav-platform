# Session 07: ArUco Detector Node

**Phase:** 2 - Perception Pipeline
**Estimated Duration:** 4-5 hours
**Difficulty:** Medium-High

---

## Prerequisites

- [ ] Session 06 complete (ArUco marker visible in camera)
- [ ] OpenCV with aruco module available
- [ ] Understand camera intrinsics (K matrix)
- [ ] Screenshot of marker from camera for testing

---

## Learning Objectives

By the end of this session, you will understand:

1. **ArUco detection pipeline** - image → corners → ID
2. **Pose estimation** - corners + intrinsics → 3D pose
3. **cv_bridge** - converting ROS Image ↔ OpenCV
4. **Detection message design** - what to publish

---

## Practical Objectives

### Primary Goal
Create uav_perception package with ArUco detector node that publishes detected targets.

### Deliverables

1. **Create `uav_perception` package:**
   ```bash
   ros2 pkg create uav_perception --build-type ament_python \
     --dependencies rclpy sensor_msgs cv_bridge uav_msgs
   ```

2. **Implement `aruco_detector.py`:**
   - Subscribe to `/camera/image_raw` and `/camera/camera_info`
   - Detect ArUco markers using cv2.aruco
   - Estimate pose using cv2.aruco.estimatePoseSingleMarkers
   - Publish to `/detection/targets` (DetectedTargetArray)
   - Optionally publish debug image with drawn markers

3. **Handle camera intrinsics:**
   - Parse CameraInfo message
   - Extract K matrix (3x3) and distortion coefficients
   - Cache for pose estimation

4. **Unit tests with saved image:**
   - Test detection on known image
   - Verify correct marker ID extracted
   - Verify pose estimation runs (even if not validating exact values)

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Create package, study cv2.aruco API |
| 0:30-1:00 | Implement image subscription with cv_bridge |
| 1:00-1:45 | Implement ArUco detection |
| 1:45-2:30 | Implement pose estimation |
| 2:30-3:00 | Create DetectedTarget messages |
| 3:00-3:30 | Write unit tests |
| 3:30-4:30 | SITL testing and debugging |
| 4:30-5:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Package builds
colcon build --packages-select uav_perception

# 2. Node runs without crash
ros2 run uav_perception aruco_detector

# 3. Detections published when marker visible
# Fly drone over marker first
ros2 topic echo /detection/targets
# Should show DetectedTargetArray with marker ID 42

# 4. Debug image shows detection (optional)
ros2 run rqt_image_view rqt_image_view
# Select /detection/debug_image, should see green box around marker

# 5. Pose makes sense
# When at (3, 3, 3) looking at marker at (3, 3, 0)
# Pose should show ~3m distance, marker below drone
```

---

## Key Questions to Answer During Session

1. What coordinate frame is the pose estimated in? (camera_optical_frame)
2. How do you convert camera-frame pose to world-frame pose? (TF)
3. What's the marker size parameter and why does it matter?
4. How reliable is pose estimation at different distances/angles?

---

## ArUco Detection Code Reference

```python
import cv2
import numpy as np
from cv_bridge import CvBridge

class ArucoDetector(Node):
    def __init__(self):
        super().__init__('aruco_detector')

        # ArUco setup
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        self.marker_size = 0.15  # meters

        # CV Bridge
        self.bridge = CvBridge()

        # Camera intrinsics (filled by callback)
        self.camera_matrix = None
        self.dist_coeffs = None

    def detect(self, cv_image):
        # Detect markers
        corners, ids, rejected = self.detector.detectMarkers(cv_image)

        if ids is not None:
            # Estimate pose for each marker
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.camera_matrix, self.dist_coeffs
            )
            return ids, corners, rvecs, tvecs
        return None, None, None, None
```

---

## Detection Message Mapping

```python
def create_detected_target(marker_id, rvec, tvec):
    target = DetectedTarget()
    target.header.stamp = self.get_clock().now().to_msg()
    target.header.frame_id = 'camera_optical_frame'

    target.target_id = f'aruco_{marker_id}'
    target.target_class = 'aruco'
    target.confidence = 1.0  # ArUco is binary (detected or not)

    # Position from tvec
    target.pose.header = target.header
    target.pose.pose.position.x = tvec[0]
    target.pose.pose.position.y = tvec[1]
    target.pose.pose.position.z = tvec[2]

    # Orientation from rvec (convert to quaternion)
    # ...

    return target
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| cv_bridge import error | Module not found | pip install cv_bridge or apt package |
| No detections | Empty array always | Check dictionary matches, lighting |
| Pose flip | Orientation jumps | ArUco ambiguity, check reprojection |
| Wrong distance | 0.5m instead of 3m | Check marker_size parameter |
| Frame mismatch | Pose in wrong location | Verify frame_id is camera_optical_frame |

---

## Code Locations

- Package: `src/uav_perception/`
- Detector: `src/uav_perception/uav_perception/aruco_detector.py`
- Tests: `src/uav_perception/test/test_aruco_detector.py`
- Test image: `src/uav_perception/test/data/aruco_test.png`

---

## Definition of Done

- [ ] uav_perception package created
- [ ] aruco_detector node implemented
- [ ] Subscribes to /camera/image_raw and /camera/camera_info
- [ ] Publishes /detection/targets (DetectedTargetArray)
- [ ] Correct marker ID extracted (42)
- [ ] Pose estimation runs
- [ ] At least 2 unit tests with saved image
- [ ] SITL: detections published when hovering over marker
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 08 will add a target tracker that smooths detections over time and handles brief detection losses.
