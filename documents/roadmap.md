# Implementation Roadmap

> **Pure task tracking document** - For architecture and design decisions, see [README.md](../README.md)

**Project:** ArUco Search & Approach Mission
**Timeline:** 16 weeks (400-500 hours at 25-30 hrs/week)
**Start Date:** Week of 2025-11-25

---

## How to Use This Document

- ✅ = Completed
- 🚧 = In Progress
- □ = Not Started

This roadmap is a **living document** - update weekly with:
- Actual progress vs planned
- Lessons learned
- Adjustments to timeline

---

## Quick Reference: Phase Overview

| Phase | Weeks | Focus | Key Milestone |
|-------|-------|-------|---------------|
| 1 | 1-3 | Foundation | Drone hovers in sim via ROS2 |
| 2 | 4-6 | Perception | ArUco detected and tracked |
| 3 | 7-9 | Simple Mission | Search mission works in SITL |
| 4 | 10-12 | Visual Servoing | Full approach mission in SITL |
| 5 | 13-14 | Integration & CI | All tests green, repeatable |
| 6 | 15-16 | Hardware | First real flight |

---

## Phase 1: Foundation (Weeks 1-3) ✅ COMPLETE

### Week 1: Development Environment & SITL Validation

**Goal:** Docker environment running ArduPilot SITL + Gazebo with verified MAVROS communication

#### Day 1-2: Docker Environment Setup (10-12 hrs)

```
□ Create project directory structure:
  autonomous_uav/
  ├── docker/
  ├── src/
  └── docs/

□ Write Dockerfile.sitl:
  - Base: osrf/ros:humble-desktop
  - Install: ArduPilot SITL, Gazebo, MAVROS
  - Install: Development tools (gdb, valgrind, htop)
  
□ Write docker-compose.yml:
  - Service: sitl (ArduPilot + Gazebo)
  - Service: ros2 (ROS2 workspace)
  - Volumes: Source code, logs
  - Network: Host mode for GUI

□ Test container builds successfully
□ Verify X11 forwarding works (for Gazebo GUI)
```

**Expected Output:** `docker-compose up` launches container with bash prompt

#### Day 3-4: ArduPilot SITL Standalone (8-10 hrs)

```
□ Start ArduPilot SITL manually:
  sim_vehicle.py -v ArduCopter -f gazebo-iris --console --map

□ Verify in MAVProxy console:
  - mode GUIDED
  - arm throttle
  - takeoff 5
  - Observe drone ascend in Gazebo
  
□ Test basic commands:
  - position (fly to coordinate)
  - land
  - RTL (return to launch)

□ Document any parameter changes needed
□ Note: If Gazebo Harmonic has issues, fall back to Gazebo Classic
```

**Expected Output:** Drone flies in Gazebo via MAVProxy commands

#### Day 5-6: MAVROS Integration (10-12 hrs)

```
□ Launch MAVROS node:
  ros2 launch mavros apm.launch fcu_url:=udp://:14550@

□ Verify topics exist:
  ros2 topic list | grep mavros
  - /mavros/state
  - /mavros/local_position/pose
  - /mavros/setpoint_position/local

□ Echo telemetry:
  ros2 topic echo /mavros/state
  ros2 topic echo /mavros/local_position/pose

□ Test arming via ROS2:
  ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

□ Test mode change:
  ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'GUIDED'}"

□ Create simple test script: arm_and_hover.py
  - Arms drone
  - Sets GUIDED mode
  - Publishes position setpoint (0, 0, 3)
  - Drone should hover at 3m

□ Document MAVROS quirks and workarounds
```

**Expected Output:** Python script makes drone hover at 3m via ROS2

#### Day 7: Unified Launch & Documentation (4-6 hrs)

```
□ Create launch file: sitl_base.launch.py
  - Launches MAVROS with correct params
  - Configurable for different FCU URLs

□ Update docker-compose for one-command startup:
  docker-compose up sitl
  # Should start Gazebo + ArduPilot + MAVROS

□ Write README for Week 1:
  - Setup instructions
  - Known issues
  - Verification commands

□ Commit to git with proper .gitignore
```

**Week 1 Deliverables:**
- [ ] Docker environment builds and runs
- [ ] ArduPilot SITL + Gazebo working
- [ ] MAVROS communication verified
- [ ] Simple hover script works
- [ ] All documented in README

**Estimated Hours:** 35-40

---

### Week 2: ROS2 Package Structure & Vehicle FSM

**Goal:** Basic package structure with working Vehicle State Machine

#### Day 1-2: Package Scaffolding (8-10 hrs)

```
□ Create ROS2 packages:
  cd src/
  ros2 pkg create autonomous_uav_msgs --build-type ament_cmake
  ros2 pkg create autonomous_uav_control --build-type ament_python
  ros2 pkg create autonomous_uav_bringup --build-type ament_python

□ Define core messages (autonomous_uav_msgs/msg/):
  
  VehicleState.msg:
  ---
  std_msgs/Header header
  uint8 flight_state        # FSM state enum
  geometry_msgs/Pose pose
  geometry_msgs/Twist velocity
  float32 battery_percent
  bool is_armed
  bool is_offboard
  string[] active_faults
  
  # Flight state constants
  uint8 STATE_UNINITIALIZED = 0
  uint8 STATE_DISARMED = 1
  uint8 STATE_ARMED = 2
  uint8 STATE_TAKING_OFF = 3
  uint8 STATE_FLYING = 4
  uint8 STATE_LANDING = 5
  uint8 STATE_LANDED = 6
  uint8 STATE_EMERGENCY = 7
  ---

□ Build and verify messages:
  colcon build --packages-select autonomous_uav_msgs
  ros2 interface show autonomous_uav_msgs/msg/VehicleState
```

**Expected Output:** Custom messages compile and are accessible

#### Day 3-4: Vehicle FSM Implementation (12-14 hrs)

```
□ Install python-statemachine:
  pip install python-statemachine

□ Create vehicle_fsm.py:
  
  class VehicleStateMachine(StateMachine):
      # States (simplified for MVP)
      uninitialized = State(initial=True)
      disarmed = State()
      armed = State()
      taking_off = State()
      flying = State()
      landing = State()
      landed = State()
      emergency = State()
      
      # Transitions with guards
      initialize = uninitialized.to(disarmed)
      arm = disarmed.to(armed, cond="pre_arm_ok")
      takeoff = armed.to(taking_off)
      altitude_reached = taking_off.to(flying)
      land = flying.to(landing)
      touched_down = landing.to(landed)
      disarm = landed.to(disarmed)
      
      # Emergency from any airborne state
      emergency_trigger = (
          armed.to(emergency) |
          taking_off.to(emergency) |
          flying.to(emergency) |
          landing.to(emergency)
      )

□ Write unit tests for FSM (test_vehicle_fsm.py):
  - Test valid transitions
  - Test invalid transitions raise errors
  - Test guard conditions
  - Test emergency transitions

□ Run tests:
  pytest src/autonomous_uav_control/test/ -v
```

**Expected Output:** FSM with 100% test coverage for transitions

#### Day 5-6: FSM ROS2 Node Integration (10-12 hrs)

```
□ Create vehicle_state_node.py (Lifecycle Node):
  
  class VehicleStateNode(LifecycleNode):
      def __init__(self):
          super().__init__('vehicle_state')
          self.fsm = VehicleStateMachine()
          
      def on_configure(self, state):
          # Subscribe to MAVROS state
          self.mavros_state_sub = self.create_subscription(
              State, '/mavros/state', self.mavros_state_cb, 10)
          
          # Publish vehicle state
          self.state_pub = self.create_publisher(
              VehicleState, '/vehicle/state', 10)
          
          # Services for state transitions
          self.arm_srv = self.create_service(
              Trigger, '/vehicle/arm', self.arm_callback)
          self.takeoff_srv = self.create_service(
              SetFloat, '/vehicle/takeoff', self.takeoff_callback)
          
      def mavros_state_cb(self, msg):
          # Sync FSM with actual vehicle state
          if msg.armed and self.fsm.current_state == self.fsm.disarmed:
              self.fsm.arm()
          # ... etc
          
      def arm_callback(self, request, response):
          try:
              self.fsm.arm()
              # Call MAVROS arm service
              response.success = True
          except TransitionNotAllowed:
              response.success = False
              response.message = "Cannot arm from current state"

□ Create launch file: vehicle_state.launch.py

□ Integration test:
  - Launch node
  - Verify state published to /vehicle/state
  - Call /vehicle/arm service
  - Verify FSM transitions
```

**Expected Output:** Vehicle state node running, publishing state, accepting commands

#### Day 7: Week 2 Integration (4-6 hrs)

```
□ Create combined launch: sitl_with_vehicle_state.launch.py
  - MAVROS
  - Vehicle State Node

□ End-to-end test:
  - Start SITL
  - Launch nodes
  - ros2 service call /vehicle/arm
  - Verify drone arms in Gazebo
  - Verify /vehicle/state shows ARMED

□ Document FSM design decisions
□ Git commit
```

**Week 2 Deliverables:**
- [ ] Package structure created
- [ ] Custom messages defined and building
- [ ] Vehicle FSM implemented with tests
- [ ] Vehicle State Node publishing state
- [ ] Arm command works via ROS2 service

**Estimated Hours:** 35-40

---

### Week 3: Vehicle Controller (Takeoff/Land)

**Goal:** Complete vehicle controller with takeoff and land actions via MAVROS services

#### Day 1-2: Vehicle Controller Node (10-12 hrs)

```
□ Create vehicle_controller.py:

  class VehicleController(LifecycleNode):
      def __init__(self):
          super().__init__('vehicle_controller')

      def on_configure(self, state):
          # MAVROS service clients for flight phase commands
          self.takeoff_client = self.create_client(
              CommandTOL, '/mavros/cmd/takeoff')
          self.land_client = self.create_client(
              CommandTOL, '/mavros/cmd/land')

          # Position setpoint publisher (for active movement only)
          self.setpoint_pub = self.create_publisher(
              PoseStamped, '/mavros/setpoint_position/local', 10)

          # Velocity setpoint publisher (for approach maneuvers)
          self.vel_pub = self.create_publisher(
              TwistStamped, '/mavros/setpoint_velocity/cmd_vel', 10)

          # Control mode flag
          self.control_mode = 'IDLE'  # IDLE, POSITION, VELOCITY

□ Understand ArduPilot GUIDED behavior:
  # CRITICAL INSIGHT: ArduPilot holds position autonomously after NAV_TAKEOFF
  # Position setpoints are ONLY needed for active movement
  # No continuous streaming required to maintain hover

□ Test MAVROS takeoff service:
  ros2 service call /mavros/cmd/takeoff mavros_msgs/srv/CommandTOL \
    "{altitude: 3.0}"
  # Verify drone takes off and holds position automatically
```

**Expected Output:** Controller node with MAVROS service clients configured

#### Day 3-4: Takeoff Action Server (10-12 hrs)

```
□ Define action (autonomous_uav_msgs/action/Takeoff.action):
  # Goal
  float32 target_altitude
  float32 timeout_sec
  ---
  # Result
  bool success
  string message
  float32 final_altitude
  ---
  # Feedback
  float32 current_altitude
  float32 progress_percent

□ Implement TakeoffActionServer:

  class TakeoffActionServer:
      def execute_callback(self, goal_handle):
          target_alt = goal_handle.request.target_altitude

          # Set mode to GUIDED
          self.set_mode('GUIDED')

          # Arm if needed
          if not self.is_armed:
              self.arm()

          # Call MAVROS takeoff service (NAV_TAKEOFF command)
          if not self._mavros_takeoff(target_alt):
              goal_handle.abort()
              return Takeoff.Result(success=False, message="NAV_TAKEOFF failed")

          # Wait for altitude reached
          while not self.altitude_reached(target_alt):
              # Publish feedback
              feedback = Takeoff.Feedback()
              feedback.current_altitude = self.current_alt
              feedback.progress_percent = (self.current_alt / target_alt) * 100
              goal_handle.publish_feedback(feedback)

              # Check timeout
              if elapsed > goal_handle.request.timeout_sec:
                  goal_handle.abort()
                  return Takeoff.Result(success=False)

              time.sleep(0.1)

          # After NAV_TAKEOFF completes, ArduPilot holds position autonomously
          goal_handle.succeed()
          return Takeoff.Result(success=True, final_altitude=self.current_alt)

□ Test takeoff action:
  ros2 action send_goal /vehicle/takeoff autonomous_uav_msgs/action/Takeoff \
    "{target_altitude: 3.0, timeout_sec: 30.0}"
```

**Expected Output:** Drone takes off to 3m via action call

#### Day 5-6: Land Action (10-12 hrs)

```
□ Define Land.action:
  # Goal
  float32 timeout_sec
  ---
  # Result
  bool success
  string message
  ---
  # Feedback
  float32 current_altitude
  uint8 landing_state  # DESCENDING, GROUND_CONTACT, DISARMED

□ Implement LandActionServer:
  - Call MAVROS land service (NAV_LAND command)
  - Monitor altitude decrease
  - Detect ground contact (altitude stable near 0)
  - Optionally disarm after landing

□ Note: HoldPosition action is NOT needed
  - ArduPilot automatically holds position in GUIDED mode
  - After takeoff, drone maintains position without continuous setpoints
  - Only need Wait/Sleep behavior for timed holds during missions

□ Integration tests for each action

□ End-to-end test script:
  async def test_full_cycle():
      await takeoff(3.0)
      # Drone holds autonomously for 5 seconds
      await asyncio.sleep(5.0)
      await land()
      # Verify drone on ground
```

**Expected Output:** Complete takeoff → autonomous hold → land cycle works

#### Day 7: Phase 1 Integration & Review (4-6 hrs)

```
□ Create master launch: sitl_full.launch.py
  - All nodes with lifecycle management
  - Proper shutdown handling

□ Run full integration test:
  - Start SITL
  - Launch all nodes
  - Execute takeoff → wait (autonomous hold) → land
  - Verify clean state transitions
  - Confirm ArduPilot maintains position without setpoints

□ Performance check:
  - CPU usage in container
  - Topic rates
  - Any dropped messages?

□ Documentation:
  - Phase 1 README
  - Architecture diagram update
  - Known issues list

□ Git tag: v0.1.0-foundation
```

**Phase 1 Deliverables:**
- ✅ Docker SITL environment working
- ✅ MAVROS communication verified
- ✅ Vehicle FSM implemented and tested
- ✅ Vehicle Controller with MAVROS service clients
- ✅ Takeoff and Land actions working via NAV_TAKEOFF/NAV_LAND
- ✅ ArduPilot autonomous hold behavior verified
- ✅ Full cycle test passes in SITL

**Phase 1 Total Hours:** 100-120

---

## Phase 2: Perception Core (Weeks 4-6) 🚧 IN PROGRESS

### Week 4: Camera Pipeline in Simulation

**Goal:** Camera images flowing from Gazebo through ROS2 pipeline

#### Day 1-2: Gazebo Camera Setup (8-10 hrs)

```
□ Create/modify Gazebo drone model with camera:
  - Camera sensor attached to drone body
  - Correct optical frame orientation (Z forward, X right)
  - Publish to /camera/image_raw and /camera/camera_info
  
□ Verify camera topics:
  ros2 topic list | grep camera
  ros2 topic hz /camera/image_raw  # Should be ~30Hz

□ View camera in rqt:
  rqt_image_view /camera/image_raw

□ Verify camera_info has correct intrinsics:
  ros2 topic echo /camera/camera_info --once
```

**Expected Output:** Camera stream visible in rqt

#### Day 3-4: Add ArUco Target to World (6-8 hrs)

```
□ Create ArUco marker model for Gazebo:
  - Flat plane with ArUco texture
  - Marker ID: 42 (or configurable)
  - Size: 0.15m (known, for pose estimation)

□ Add marker to world at known position:
  - Position: (2, 0, 0.5)  # 2m in front, 0.5m high

□ Verify marker visible in camera when drone hovers:
  - Start SITL
  - Takeoff to 3m
  - Rotate to face marker
  - Capture frame, verify marker visible

□ Create second world file with marker at different position for testing
```

**Expected Output:** ArUco marker visible in simulated camera

#### Day 5-6: Image Transport & Frame Management (8-10 hrs)

```
□ Understand ROS2 camera frame conventions:
  - Camera optical frame: Z forward, X right, Y down
  - Body frame: X forward, Y left, Z up
  - World frame: NED or ENU (ArduPilot uses NED)

□ Verify TF tree:
  ros2 run tf2_tools view_frames
  - base_link → camera_link → camera_optical_frame

□ Create camera test node:
  - Subscribe to /camera/image_raw
  - Convert with cv_bridge
  - Display with OpenCV
  - Verify images are correct (not rotated, flipped, etc.)

□ Test different lighting conditions in Gazebo (if needed later)
```

**Expected Output:** TF tree correct, images flowing through cv_bridge

#### Day 7: Week 4 Integration (4-5 hrs)

```
□ Update launch files to include camera
□ Document camera setup and frame conventions
□ Create test: camera_pipeline_test.py
  - Verifies images received
  - Verifies camera_info matches
  - Verifies TF published
□ Git commit
```

**Week 4 Deliverables:**
- [ ] Gazebo camera publishing images
- [ ] ArUco marker in simulation world
- [ ] TF tree correct
- [ ] Camera test node working

**Estimated Hours:** 30-35

---

### Week 5: ArUco Detector Implementation

**Goal:** Working ArUco detection with pose estimation

#### Day 1-2: ArUco Detector Node (10-12 hrs)

```
□ Create target_detector package:
  ros2 pkg create autonomous_uav_perception --build-type ament_python

□ Define detection messages:
  
  DetectedTarget.msg:
  ---
  std_msgs/Header header
  string target_id          # "aruco_42"
  string target_class       # "aruco"
  geometry_msgs/PoseStamped pose_camera_frame
  float32 confidence        # Always 1.0 for ArUco
  float32[4] bounding_box   # [x, y, w, h] normalized
  ---
  
  DetectedTargetArray.msg:
  ---
  std_msgs/Header header
  DetectedTarget[] targets
  ---

□ Implement aruco_detector.py:
  
  class ArucoDetector(Node):
      def __init__(self):
          super().__init__('aruco_detector')
          
          # Parameters
          self.declare_parameter('dictionary', 'DICT_4X4_50')
          self.declare_parameter('marker_size_m', 0.15)
          
          # ArUco setup
          self.aruco_dict = cv2.aruco.getPredefinedDictionary(
              cv2.aruco.DICT_4X4_50)
          self.aruco_params = cv2.aruco.DetectorParameters()
          self.detector = cv2.aruco.ArucoDetector(
              self.aruco_dict, self.aruco_params)
          
          # Subscribers
          self.image_sub = self.create_subscription(
              Image, '/camera/image_raw', self.image_callback, 10)
          self.camera_info_sub = ...
          
          # Publishers
          self.detection_pub = self.create_publisher(
              DetectedTargetArray, '/detection/targets', 10)

□ Implement image_callback:
  def image_callback(self, msg):
      cv_image = self.bridge.imgmsg_to_cv2(msg)
      corners, ids, rejected = self.detector.detectMarkers(cv_image)
      
      if ids is not None:
          # Estimate pose for each marker
          rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
              corners, self.marker_size, 
              self.camera_matrix, self.dist_coeffs)
          
          # Convert to DetectedTarget messages
          targets = []
          for i, marker_id in enumerate(ids.flatten()):
              target = DetectedTarget()
              target.target_id = f"aruco_{marker_id}"
              target.pose_camera_frame = self.rvec_tvec_to_pose(
                  rvecs[i], tvecs[i])
              targets.append(target)
          
          self.detection_pub.publish(DetectedTargetArray(targets=targets))
```

**Expected Output:** Detection messages published when marker visible

#### Day 3-4: Pose Estimation & Frame Transforms (10-12 hrs)

```
□ Implement rvec/tvec to PoseStamped conversion:
  def rvec_tvec_to_pose(self, rvec, tvec, header):
      pose = PoseStamped()
      pose.header = header
      pose.header.frame_id = "camera_optical_frame"
      
      # Position from tvec
      pose.pose.position.x = tvec[0][0]
      pose.pose.position.y = tvec[0][1]
      pose.pose.position.z = tvec[0][2]
      
      # Orientation from rvec (Rodrigues to quaternion)
      rotation_matrix, _ = cv2.Rodrigues(rvec)
      quat = transforms3d.quaternions.mat2quat(rotation_matrix)
      pose.pose.orientation.w = quat[0]
      pose.pose.orientation.x = quat[1]
      pose.pose.orientation.y = quat[2]
      pose.pose.orientation.z = quat[3]
      
      return pose

□ Add TF broadcast for detected targets:
  - Broadcast transform: camera_optical_frame → aruco_42
  - Visualize in RViz

□ Transform to world frame:
  - Use tf2_ros to lookup camera → world transform
  - Transform target pose to world frame
  - Publish both camera frame and world frame poses

□ Unit tests with known images:
  - Load test image with ArUco marker
  - Verify detection
  - Verify pose within tolerance
```

**Expected Output:** Target poses in both camera and world frames

#### Day 5-6: Debug Visualization (8-10 hrs)

```
□ Add debug image publisher:
  def publish_debug_image(self, cv_image, corners, ids, rvecs, tvecs):
      # Draw detected markers
      cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)
      
      # Draw axes for pose
      for rvec, tvec in zip(rvecs, tvecs):
          cv2.drawFrameAxes(cv_image, self.camera_matrix, 
              self.dist_coeffs, rvec, tvec, 0.1)
      
      # Publish
      debug_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
      self.debug_pub.publish(debug_msg)

□ RViz visualization:
  - Add camera display
  - Add TF display for aruco markers
  - Add MarkerArray for detected targets

□ Create RViz config file for debugging

□ Parameter tuning:
  - Test detection at various distances (0.5m - 5m)
  - Test detection at various angles
  - Document reliable detection envelope
```

**Expected Output:** Visual debugging working, detection envelope documented

#### Day 7: Integration Testing (4-5 hrs)

```
□ End-to-end perception test:
  - Start SITL with marker world
  - Launch detector
  - Takeoff and rotate toward marker
  - Verify detections published
  - Verify poses accurate (compare to ground truth)

□ Performance testing:
  - Detection rate (should be ~camera rate)
  - CPU usage
  - Latency (image timestamp to detection timestamp)

□ Document detection parameters and tuning

□ Git commit
```

**Week 5 Deliverables:**
- [ ] ArUco detector node working
- [ ] Pose estimation accurate
- [ ] TF broadcast for targets
- [ ] Debug visualization
- [ ] Performance acceptable

**Estimated Hours:** 35-40

---

### Week 6: Target Tracking & State Estimation

**Goal:** Temporal filtering and track persistence for detected targets

#### Day 1-2: Simple Target Tracker (10-12 hrs)

```
□ Design tracker requirements:
  - Smooth noisy detections (low-pass filter)
  - Maintain track when target temporarily occluded (0.5-1s)
  - Handle multiple targets (for future)
  - Output "tracking confidence" (detection age, consistency)

□ Implement target_tracker.py:
  
  class TargetTracker(Node):
      def __init__(self):
          self.tracks = {}  # target_id → Track
          
      class Track:
          def __init__(self, target_id, initial_pose):
              self.target_id = target_id
              self.pose = initial_pose
              self.velocity = Twist()  # For prediction
              self.last_seen = time.time()
              self.detection_count = 0
              self.alpha = 0.3  # Low-pass filter coefficient
              
          def update(self, new_pose):
              # Exponential moving average for smoothing
              self.pose.position.x = (
                  self.alpha * new_pose.position.x + 
                  (1 - self.alpha) * self.pose.position.x)
              # ... same for y, z
              
              self.last_seen = time.time()
              self.detection_count += 1
              
          def predict(self, dt):
              # Simple constant-velocity prediction
              self.pose.position.x += self.velocity.linear.x * dt
              # ... etc
              
          def is_stale(self, timeout=1.0):
              return (time.time() - self.last_seen) > timeout

□ Implement tracking loop:
  def detection_callback(self, msg):
      current_time = time.time()
      seen_ids = set()
      
      for target in msg.targets:
          seen_ids.add(target.target_id)
          
          if target.target_id in self.tracks:
              self.tracks[target.target_id].update(target.pose)
          else:
              self.tracks[target.target_id] = Track(
                  target.target_id, target.pose)
      
      # Predict unseen tracks
      for tid, track in self.tracks.items():
          if tid not in seen_ids:
              track.predict(dt)
      
      # Remove stale tracks
      self.tracks = {
          k: v for k, v in self.tracks.items() 
          if not v.is_stale()
      }
      
      # Publish tracked targets
      self.publish_tracked_targets()
```

**Expected Output:** Smoothed target positions with track persistence

#### Day 3-4: State Estimator Node (10-12 hrs)

```
□ Create state_estimator.py - central world model:
  
  class StateEstimator(LifecycleNode):
      """Fuses vehicle state and target state into unified world model."""
      
      def on_configure(self, state):
          # Vehicle state from MAVROS
          self.vehicle_pose_sub = self.create_subscription(
              PoseStamped, '/mavros/local_position/pose', ...)
          self.vehicle_vel_sub = self.create_subscription(
              TwistStamped, '/mavros/local_position/velocity_local', ...)
          
          # Target tracks
          self.target_sub = self.create_subscription(
              DetectedTargetArray, '/detection/targets', ...)
          
          # Unified state output
          self.world_state_pub = self.create_publisher(
              WorldState, '/world/state', 10)
          
      def publish_world_state(self):
          state = WorldState()
          state.vehicle = self.vehicle_state
          state.tracked_targets = list(self.target_tracker.tracks.values())
          state.primary_target = self.get_primary_target()
          self.world_state_pub.publish(state)

□ Define WorldState.msg:
  std_msgs/Header header
  VehicleState vehicle
  TrackedTarget[] targets
  TrackedTarget primary_target  # Current mission target
  bool target_locked

□ Implement primary target selection:
  - If only one target, it's primary
  - If multiple, select by mission criteria (e.g., specific ID)
  - Sticky selection (don't switch rapidly)
```

**Expected Output:** WorldState message with fused data

#### Day 5-6: Integration & Testing (8-10 hrs)

```
□ Integration test: full perception pipeline
  - Camera → Detector → Tracker → State Estimator → WorldState

□ Occlusion handling test:
  - Detect target
  - Block camera briefly (or fly past)
  - Verify track persists for ~1s
  - Verify track removed after timeout

□ Noise rejection test:
  - Measure raw detection pose variance
  - Measure tracked pose variance
  - Should be significantly smoother

□ Multi-target test:
  - Add second ArUco marker to world
  - Verify both tracked independently
  - Verify primary selection works

□ Create state_estimator.launch.py

□ Update full launch to include perception pipeline
```

**Expected Output:** Complete perception pipeline tested

#### Day 7: Phase 2 Review (4-5 hrs)

```
□ Full pipeline test:
  - Start SITL
  - Launch all nodes (vehicle + perception)
  - Takeoff
  - Rotate toward marker
  - Verify WorldState shows locked target
  - Land

□ Performance profiling:
  - Overall CPU usage
  - Per-node CPU usage
  - Message rates

□ Documentation:
  - Perception architecture diagram
  - Parameter reference
  - Tuning guide

□ Git tag: v0.2.0-perception
```

**Phase 2 Deliverables:**
- [ ] Camera pipeline from Gazebo working
- [ ] ArUco marker in simulation
- [ ] Detector with pose estimation
- [ ] Target tracker with smoothing
- [ ] State estimator with WorldState
- [ ] Full pipeline tested

**Phase 2 Total Hours:** 100-120

---

## Phase 3: Simple Mission (Weeks 7-9)

### Week 7: Behavior Tree Framework

**Goal:** py_trees integrated with basic behaviors

#### Day 1-2: py_trees Setup & Learning (8-10 hrs)

```
□ Install py_trees and py_trees_ros:
  pip install py_trees py_trees_ros_interfaces
  # py_trees_ros from source for ROS2 Humble

□ Tutorial exercises:
  - Create simple BT with Sequence/Fallback
  - Understand tick() mechanism
  - Understand Blackboard (shared state)
  - Practice with py_trees viewer

□ Create mission package:
  ros2 pkg create autonomous_uav_mission --build-type ament_python

□ Create basic BT test:
  # Simple: Success → Success → Success (sequence)
  # Verify all tick correctly
```

**Expected Output:** py_trees understood, test BT running

#### Day 3-4: ROS2 Behavior Wrappers (10-12 hrs)

```
□ Create base classes for ROS2 integration:
  
  class RosActionBehavior(py_trees.behaviour.Behaviour):
      """Base class for behaviors that call ROS2 actions."""
      
      def __init__(self, name, action_type, action_name, goal):
          super().__init__(name)
          self.action_client = None
          self.goal_handle = None
          
      def initialise(self):
          # Send goal
          self.goal_handle = self.action_client.send_goal_async(self.goal)
          
      def update(self):
          if self.goal_handle is None:
              return py_trees.Status.RUNNING
          
          if not self.goal_handle.done():
              return py_trees.Status.RUNNING
              
          result = self.goal_handle.result()
          if result.success:
              return py_trees.Status.SUCCESS
          else:
              return py_trees.Status.FAILURE
              
      def terminate(self, new_status):
          if new_status == py_trees.Status.INVALID:
              # Cancel goal if preempted
              if self.goal_handle:
                  self.goal_handle.cancel_goal_async()

□ Create RosCondition base class:
  class RosCondition(py_trees.behaviour.Behaviour):
      """Checks condition from ROS topic."""
      
      def update(self):
          if self.check_condition():
              return py_trees.Status.SUCCESS
          return py_trees.Status.FAILURE
```

**Expected Output:** Reusable base classes for ROS2 behaviors

#### Day 5-6: Core Behaviors (10-12 hrs)

```
□ Implement TakeoffBehavior:
  class TakeoffBehavior(RosActionBehavior):
      def __init__(self, name, altitude):
          goal = Takeoff.Goal(target_altitude=altitude, timeout_sec=30.0)
          super().__init__(name, Takeoff, '/vehicle/takeoff', goal)

□ Implement LandBehavior:
  class LandBehavior(RosActionBehavior):
      # Similar pattern

□ Implement WaitBehavior:
  class WaitBehavior(py_trees.behaviour.Behaviour):
      # Simple time-based wait (ArduPilot holds autonomously)

□ Implement conditions:
  class IsArmed(RosCondition):
      def check_condition(self):
          return self.blackboard.vehicle_state.is_armed
          
  class TargetDetected(RosCondition):
      def check_condition(self):
          return self.blackboard.world_state.target_locked

□ Test each behavior individually:
  - TakeoffBehavior takes off and returns SUCCESS
  - LandBehavior lands and returns SUCCESS
  - WaitBehavior waits for duration (drone holds autonomously)
  - IsArmed returns SUCCESS when armed
```

**Expected Output:** All basic behaviors working independently

#### Day 7: Simple Sequence Test (4-5 hrs)

```
□ Create simple mission tree:
  root = py_trees.composites.Sequence("simple_mission", memory=True)
  root.add_children([
      TakeoffBehavior("takeoff", altitude=3.0),
      WaitBehavior("wait", duration=5.0),
      LandBehavior("land")
  ])

□ Test in SITL:
  - Mission runs start to finish
  - Each behavior completes correctly
  - Tree status visible in py_trees viewer

□ Document behavior interface patterns
□ Git commit
```

**Week 7 Deliverables:**
- [ ] py_trees integrated
- [ ] ROS2 behavior base classes
- [ ] Takeoff, Land, Wait behaviors
- [ ] Simple sequence mission works

**Estimated Hours:** 35-40

---

### Week 8: Search Behavior

**Goal:** Rotate search pattern that finds ArUco marker

#### Day 1-2: Yaw Control Implementation (8-10 hrs)

```
□ Add yaw setpoint to VehicleController:
  def set_yaw(self, yaw_rad, relative=False):
      """Set target yaw angle."""
      if relative:
          yaw_rad = self.current_yaw + yaw_rad
      self.target_yaw = yaw_rad
      # Update setpoint to include yaw

□ Verify yaw control in SITL:
  - Takeoff
  - Command 90° yaw
  - Verify drone rotates
  - Measure accuracy and settling time

□ Create YawAction (simple action for specific yaw):
  YawTo.action:
    float32 target_yaw_deg
    float32 yaw_rate_deg_s
    float32 tolerance_deg
    ---
    bool success
    float32 final_yaw_deg
    ---
    float32 current_yaw_deg
    float32 error_deg
```

**Expected Output:** Yaw control working via action

#### Day 3-4: Rotate Search Behavior (12-14 hrs)

```
□ Implement RotateSearchBehavior:
  
  class RotateSearchBehavior(py_trees.behaviour.Behaviour):
      """Rotates incrementally until target detected."""
      
      def __init__(self, name, yaw_step_deg=30, pause_sec=2.0, max_rotations=12):
          super().__init__(name)
          self.yaw_step = math.radians(yaw_step_deg)
          self.pause_sec = pause_sec
          self.max_rotations = max_rotations
          
      def initialise(self):
          self.rotation_count = 0
          self.state = 'ROTATING'  # ROTATING, PAUSING, CHECKING
          self.pause_start = None
          
      def update(self):
          # Check if target found (always check first)
          if self.blackboard.world_state.target_locked:
              return py_trees.Status.SUCCESS
          
          # Check rotation limit
          if self.rotation_count >= self.max_rotations:
              return py_trees.Status.FAILURE  # Target not found
          
          if self.state == 'ROTATING':
              # Command yaw increment
              self.controller.yaw_increment(self.yaw_step)
              self.state = 'WAITING_YAW'
              
          elif self.state == 'WAITING_YAW':
              if self.yaw_reached():
                  self.state = 'PAUSING'
                  self.pause_start = time.time()
                  
          elif self.state == 'PAUSING':
              # Wait for detection opportunity
              if time.time() - self.pause_start > self.pause_sec:
                  self.rotation_count += 1
                  self.state = 'ROTATING'
          
          return py_trees.Status.RUNNING

□ Test rotate search:
  - Place marker at random angle
  - Verify drone rotates until found
  - Verify stops when target detected
  - Verify fails after max rotations if no target
```

**Expected Output:** Rotate search finds target reliably

#### Day 5-6: Search Fallback Pattern (8-10 hrs)

```
□ Implement search fallback tree:
  
  search_subtree = py_trees.composites.Fallback("search", memory=False)
  search_subtree.add_children([
      TargetDetected("target_visible"),  # If already visible, succeed
      RotateSearchBehavior("rotate_search")
  ])
  
  # Fallback semantics:
  # - If TargetDetected returns SUCCESS, done
  # - Otherwise, try RotateSearch
  # - If RotateSearch succeeds (found), done
  # - If RotateSearch fails (not found), Fallback fails

□ Test fallback:
  - Case 1: Target already visible → immediate success
  - Case 2: Target not visible → rotate until found → success
  - Case 3: No target in world → rotate 360° → failure

□ Add "search altitude" behavior:
  - If not at search altitude, go there first
  - Then search

□ Create search_and_detect mission:
  root = Sequence([
      TakeoffBehavior(alt=3.0),
      search_subtree,
      WaitBehavior(duration=3.0),  # Celebrate finding target (drone holds autonomously)
      LandBehavior()
  ])
```

**Expected Output:** Search & detect mission completes

#### Day 7: Week 8 Integration (4-5 hrs)

```
□ Full search mission test (5 runs):
  - Randomize marker position each run
  - Verify success rate > 90%
  - Measure average time to find

□ Edge case testing:
  - Target behind drone (requires 180° rotation)
  - Target at edge of camera FOV
  - Multiple targets in scene

□ Performance tuning:
  - Optimize yaw_step for detection reliability vs speed
  - Tune pause_sec for detection latency

□ Documentation & git commit
```

**Week 8 Deliverables:**
- [ ] Yaw control working
- [ ] RotateSearchBehavior implemented
- [ ] Search fallback pattern
- [ ] Search & detect mission tested

**Estimated Hours:** 35-40

---

### Week 9: Mission Executor & Full Simple Mission

**Goal:** Mission executor node running complete simple mission

#### Day 1-2: Mission Executor Node (10-12 hrs)

```
□ Create mission_executor.py (Lifecycle Node):
  
  class MissionExecutor(LifecycleNode):
      def __init__(self):
          super().__init__('mission_executor')
          
      def on_configure(self, state):
          # Blackboard setup
          self.blackboard = py_trees.blackboard.Client()
          self.blackboard.register_key(
              key="world_state", access=py_trees.common.Access.WRITE)
          self.blackboard.register_key(
              key="vehicle_state", access=py_trees.common.Access.WRITE)
          
          # World state subscriber
          self.world_sub = self.create_subscription(
              WorldState, '/world/state', self.world_state_cb, 10)
          
          # Mission action server
          self.mission_server = ActionServer(
              self, ExecuteMission, '/mission/execute',
              execute_callback=self.execute_mission)
          
          # Load behavior tree
          self.tree = self.load_tree()
          
      def on_activate(self, state):
          # Start BT tick timer
          self.tick_timer = self.create_timer(0.1, self.tick_tree)  # 10Hz
          
      def tick_tree(self):
          self.tree.tick_once()
          # Publish status
          self.publish_mission_status()

□ Implement mission loading from XML (optional for MVP):
  # For now, hardcode tree in Python
  # Later: load from BT XML file
```

**Expected Output:** Mission executor node structure complete

#### Day 3-4: Full Simple Mission (10-12 hrs)

```
□ Assemble complete "search and detect" mission tree:
  
  def create_search_detect_tree():
      root = py_trees.composites.Sequence("search_detect", memory=True)
      
      # Pre-conditions
      arm_check = IsArmed("check_armed")
      
      # Takeoff
      takeoff = TakeoffBehavior("takeoff", altitude=3.0)
      
      # Search (with fallback)
      search = py_trees.composites.Fallback("search", memory=False)
      search.add_children([
          TargetDetected("already_visible"),
          RotateSearchBehavior("rotate_search", 
              yaw_step_deg=30, pause_sec=2.0, max_rotations=12)
      ])
      
      # Wait at target (ArduPilot holds position autonomously)
      wait = WaitBehavior("wait_at_target", duration=5.0)
      
      # Land
      land = LandBehavior("land")
      
      root.add_children([arm_check, takeoff, search, wait, land])
      return root

□ Test complete mission:
  - Arm
  - ros2 action send_goal /mission/execute ...
  - Watch mission execute
  - Verify all phases complete
```

**Expected Output:** Complete mission runs start to finish

#### Day 5-6: Error Handling & Recovery (8-10 hrs)

```
□ Add timeout decorators:
  from py_trees.decorators import Timeout
  
  takeoff_with_timeout = Timeout(
      "takeoff_timeout",
      child=TakeoffBehavior("takeoff", altitude=3.0),
      duration=30.0)

□ Add retry for search:
  from py_trees.decorators import Retry
  
  search_with_retry = Retry(
      "search_retry",
      child=search_subtree,
      num_failures=2)  # Try twice before giving up

□ Add failure handling:
  # If search fails completely, land safely
  mission_with_recovery = py_trees.composites.Selector("mission", memory=True)
  mission_with_recovery.add_children([
      main_mission_sequence,
      SafeLandBehavior("emergency_land")  # Fallback if mission fails
  ])

□ Test failure scenarios:
  - Search timeout (no marker) → lands safely
  - Takeoff timeout → aborts cleanly
  - Low battery during search → emergency behavior (future)
```

**Expected Output:** Mission handles failures gracefully

#### Day 7: Phase 3 Review (4-5 hrs)

```
□ Full mission test suite (automated):
  - test_mission_success: Normal completion
  - test_mission_search_timeout: No target found
  - test_mission_takeoff_timeout: Takeoff fails
  - test_mission_cancel: User cancels mid-mission

□ Performance profiling:
  - Mission execution time
  - BT tick rate stability
  - CPU usage during mission

□ Documentation:
  - BT design patterns used
  - Mission flow diagram
  - Adding new behaviors guide

□ Git tag: v0.3.0-simple-mission
```

**Phase 3 Deliverables:**
- [ ] py_trees framework integrated
- [ ] All basic behaviors working
- [ ] Rotate search behavior
- [ ] Mission executor node
- [ ] Complete search & detect mission
- [ ] Error handling with recovery

**Phase 3 Total Hours:** 100-120

---

## Phase 4: Visual Servoing (Weeks 10-12)

### Week 10: Approach Controller Design

**Goal:** Working approach controller in simulation

#### Day 1-2: Visual Servoing Theory (6-8 hrs)

```
□ Study visual servoing basics:
  - Image-Based Visual Servoing (IBVS) vs Position-Based (PBVS)
  - We'll use PBVS (simpler for known target size)
  - Error = desired_position - current_target_position
  - Control = f(error) → velocity command

□ Design approach controller:
  
  PBVS Controller:
  - Target: ArUco marker at known world position (from detection)
  - Desired: Drone positioned X meters in front of target
  - Error: Vector from drone to desired position
  - Output: Velocity command to reduce error
  
  Approach phases:
  1. ORIENT: Turn to face target
  2. APPROACH: Move toward target
  3. HOLD: Maintain position at target distance

□ Define approach parameters:
  - target_distance_m: 1.0 (distance to maintain from target)
  - approach_speed_m_s: 0.3 (max approach velocity)
  - angular_gain: 0.5 (yaw correction gain)
  - linear_gain: 0.3 (position correction gain)
```

**Expected Output:** Clear design for approach controller

#### Day 3-5: Approach Controller Implementation (16-20 hrs)

```
□ Create approach_controller.py:
  
  class ApproachController:
      def __init__(self):
          self.target_distance = 1.0
          self.max_speed = 0.3
          self.kp_linear = 0.3
          self.kp_angular = 0.5
          
      def compute_velocity(self, drone_pose, target_pose):
          """Compute velocity to approach target."""
          
          # Vector from drone to target (in world frame)
          dx = target_pose.position.x - drone_pose.position.x
          dy = target_pose.position.y - drone_pose.position.y
          dz = target_pose.position.z - drone_pose.position.z
          
          # Distance to target
          distance = math.sqrt(dx*dx + dy*dy + dz*dz)
          
          # Bearing to target
          target_yaw = math.atan2(dy, dx)
          
          # Current yaw
          current_yaw = self.quaternion_to_yaw(drone_pose.orientation)
          
          # Yaw error
          yaw_error = self.normalize_angle(target_yaw - current_yaw)
          
          # Distance error (how far we are from desired distance)
          distance_error = distance - self.target_distance
          
          # Compute velocities
          vel = TwistStamped()
          
          # Angular (yaw) velocity - always correct heading
          vel.twist.angular.z = self.kp_angular * yaw_error
          
          # Linear velocity - only if roughly facing target
          if abs(yaw_error) < math.radians(30):
              # Forward velocity (in body frame)
              forward_vel = self.kp_linear * distance_error
              forward_vel = max(-self.max_speed, min(self.max_speed, forward_vel))
              vel.twist.linear.x = forward_vel
          
          return vel, {
              'distance': distance,
              'yaw_error': yaw_error,
              'distance_error': distance_error
          }

□ Create ApproachAction server:
  - Goal: target_id, target_distance, approach_speed, timeout
  - Feedback: distance, yaw_error, phase (ORIENT/APPROACH/HOLD)
  - Result: success, final_distance, message

□ Test approach controller:
  - Start 5m from target
  - Run approach
  - Verify drone moves toward target
  - Verify stops at target_distance
```

**Expected Output:** Approach controller moves drone toward target

#### Day 6-7: Approach Tuning & Edge Cases (8-10 hrs)

```
□ Tune controller gains in simulation:
  - Start with conservative gains (0.2-0.3)
  - Increase until oscillation, then back off
  - Document final gains

□ Test edge cases:
  - Target at extreme angle (requires large yaw correction)
  - Target very close (should back up)
  - Target moving (future: track moving target)
  - Target lost during approach

□ Add target lost handling:
  - If target not seen for >1s, abort approach
  - Return FAILURE for BT to handle

□ Performance verification:
  - Approach accuracy (how close to target_distance)
  - Settling time
  - Overshoot

□ Document approach parameters
```

**Week 10 Deliverables:**
- [ ] Approach controller designed
- [ ] PBVS implementation working
- [ ] Controller gains tuned
- [ ] Edge cases handled

**Estimated Hours:** 35-40

---

### Week 11: Approach Behavior & Integration

**Goal:** Approach behavior integrated into full mission

#### Day 1-2: Approach Behavior (8-10 hrs)

```
□ Create ApproachTargetBehavior:
  
  class ApproachTargetBehavior(py_trees.behaviour.Behaviour):
      def __init__(self, name, target_distance=1.0, timeout=60.0):
          super().__init__(name)
          self.target_distance = target_distance
          self.timeout = timeout
          
      def initialise(self):
          self.start_time = time.time()
          self.approach_action = ApproachAction.Goal(
              target_id=self.blackboard.primary_target.target_id,
              target_distance_m=self.target_distance,
              timeout_sec=self.timeout)
          self.goal_handle = self.action_client.send_goal_async(self.approach_action)
          
      def update(self):
          # Check timeout
          if time.time() - self.start_time > self.timeout:
              return py_trees.Status.FAILURE
          
          # Check action status
          if self.goal_handle.done():
              if self.goal_handle.result().success:
                  return py_trees.Status.SUCCESS
              return py_trees.Status.FAILURE
          
          return py_trees.Status.RUNNING
          
      def terminate(self, new_status):
          if new_status == py_trees.Status.INVALID:
              self.goal_handle.cancel_goal_async()

□ Test approach behavior in isolation:
  - Setup: Drone hovering, target visible
  - Run approach behavior
  - Verify completes successfully
```

**Expected Output:** Approach behavior works standalone

#### Day 3-4: Full Mission Assembly (10-12 hrs)

```
□ Create complete ArUco Search & Approach mission:
  
  def create_aruco_mission():
      root = Sequence("aruco_mission", memory=True)
      
      # Pre-flight
      precheck = Sequence("precheck", memory=True)
      precheck.add_children([
          IsArmed("armed_check"),
          BatteryOk("battery_check"),  # Future
      ])
      
      # Takeoff
      takeoff = Timeout("takeoff_timeout",
          child=TakeoffBehavior("takeoff", altitude=3.0),
          duration=30.0)
      
      # Search
      search = Fallback("search", memory=False)
      search.add_children([
          TargetDetected("already_visible"),
          Retry("search_retry",
              child=RotateSearchBehavior("rotate", yaw_step_deg=30),
              num_failures=2)
      ])
      
      # Approach
      approach = Timeout("approach_timeout",
          child=ApproachTargetBehavior("approach", target_distance=1.0),
          duration=60.0)
      
      # Wait at target (ArduPilot holds position autonomously)
      wait = WaitBehavior("wait", duration=10.0)
      
      # Land
      land = LandBehavior("land")
      
      root.add_children([precheck, takeoff, search, approach, wait, land])
      
      # Wrap in recovery
      mission_with_recovery = Selector("mission_safe", memory=True)
      mission_with_recovery.add_children([
          root,
          SafeLandBehavior("emergency_land")
      ])
      
      return mission_with_recovery

□ Test full mission in SITL:
  - Place target at random position
  - Run mission
  - Verify all phases complete
  - Measure total mission time
```

**Expected Output:** Full mission runs successfully

#### Day 5-6: Mission Variations & Robustness (8-10 hrs)

```
□ Test mission robustness:
  - 10 randomized runs
  - Vary target position
  - Vary starting position
  - Document success rate

□ Test failure recovery:
  - Target disappears mid-approach → should abort, land safely
  - Approach timeout → should land safely
  - Search fails → should land safely

□ Add mission status publishing:
  MissionStatus.msg:
    string mission_id
    string current_phase  # TAKEOFF, SEARCH, APPROACH, HOLD, LAND
    string current_behavior
    float32 progress_percent
    string[] active_warnings

□ Create RViz visualization for mission status
```

**Expected Output:** Robust mission with status feedback

#### Day 7: Week 11 Review (4-5 hrs)

```
□ Full integration test:
  - Start from docker-compose up
  - Launch all nodes
  - Run mission
  - Verify clean completion

□ Performance metrics:
  - Mission completion rate (should be >95%)
  - Average mission time
  - Approach accuracy

□ Documentation update
□ Git commit
```

**Week 11 Deliverables:**
- [ ] Approach behavior integrated
- [ ] Full mission working
- [ ] Failure recovery tested
- [ ] Mission status publishing

**Estimated Hours:** 35-40

---

### Week 12: Polish & Edge Cases

**Goal:** Mission reliable in all tested scenarios

#### Day 1-3: Edge Case Testing & Fixes (15-18 hrs)

```
□ Systematic edge case testing:
  
  Target position variations:
  □ Target directly behind (180° turn required)
  □ Target at 5m (max reliable detection distance)
  □ Target at 0.5m (very close)
  □ Target at different heights (ground level, eye level, above)
  
  Lighting variations (in Gazebo):
  □ Bright sunlight
  □ Low light (if Gazebo supports)
  □ Target in shadow
  
  Mission interruptions:
  □ Cancel mid-takeoff
  □ Cancel mid-search
  □ Cancel mid-approach
  □ All should result in safe landing
  
  Error conditions:
  □ MAVROS disconnect simulation
  □ Camera failure simulation
  □ Detection timeout

□ Fix any issues discovered
□ Add regression tests for each fixed bug
```

**Expected Output:** All edge cases handled

#### Day 4-5: Parameter Optimization (8-10 hrs)

```
□ Optimize search parameters:
  - yaw_step_deg: Balance speed vs detection reliability
  - pause_sec: Minimum for reliable detection
  - Test: Time to find target vs reliability

□ Optimize approach parameters:
  - Gains: Fastest approach without overshoot
  - target_distance: Minimum reliable distance
  - Test: Approach accuracy and settling time

□ Create parameter presets:
  - conservative.yaml: Slow but very reliable
  - balanced.yaml: Default
  - aggressive.yaml: Fast but requires good conditions

□ Document parameter effects
```

**Expected Output:** Optimized parameters with presets

#### Day 6-7: Phase 4 Review (6-8 hrs)

```
□ Comprehensive test suite:
  - 20 randomized mission runs
  - Document success rate, timing, issues

□ Video recording of successful mission:
  - Screen capture of Gazebo
  - Screen capture of RViz
  - Narrated explanation (for portfolio)

□ Documentation:
  - Mission flow diagram (updated)
  - Parameter reference
  - Troubleshooting guide

□ Code review:
  - Clean up TODOs
  - Improve logging
  - Add docstrings

□ Git tag: v0.4.0-full-mission
```

**Phase 4 Deliverables:**
- [ ] Visual servoing approach working
- [ ] Full mission reliable
- [ ] Edge cases handled
- [ ] Parameters optimized
- [ ] Video demo recorded

**Phase 4 Total Hours:** 100-120

---

## Phase 5: Integration & CI (Weeks 13-14)

### Week 13: Testing Infrastructure

**Goal:** Automated test suite with CI pipeline

#### Day 1-2: Unit Test Suite (10-12 hrs)

```
□ Unit tests for each component:
  
  test_vehicle_fsm.py:
  - All valid transitions
  - Invalid transition rejection
  - Guard conditions
  - Coverage: 100%
  
  test_aruco_detector.py:
  - Detection with known test images
  - Pose estimation accuracy
  - No detection when no marker
  - Coverage: 80%+
  
  test_target_tracker.py:
  - Track creation
  - Track update (smoothing)
  - Track persistence (occlusion)
  - Track removal (timeout)
  - Coverage: 80%+
  
  test_approach_controller.py:
  - Velocity computation
  - Edge cases (target behind, very close)
  - Coverage: 80%+

□ Run all tests:
  pytest src/ --cov --cov-report=html
  
□ Fix any coverage gaps
```

**Expected Output:** >80% overall code coverage

#### Day 3-4: Integration Tests (10-12 hrs)

```
□ Create integration tests using launch_testing:
  
  test_perception_pipeline.py:
  - Launch camera sim, detector, tracker
  - Publish test images
  - Verify detections match expected
  
  test_control_pipeline.py:
  - Launch vehicle controller with mock MAVROS
  - Send commands
  - Verify setpoints published correctly
  
  test_mission_executor.py:
  - Launch mission executor with mock behaviors
  - Verify behavior tree execution
  - Verify status publishing

□ Add to CMakeLists.txt / setup.py:
  ament_add_pytest_test(
      integration_perception
      test/integration/test_perception_pipeline.py
      TIMEOUT 60
  )
```

**Expected Output:** Integration tests passing

#### Day 5-6: SITL System Tests (10-12 hrs)

```
□ Create SITL test framework:
  
  class SitlTestCase:
      def setup(self):
          # Start SITL + all nodes
          self.launch_sitl()
          self.wait_for_ready()
          
      def teardown(self):
          self.collect_logs()
          self.shutdown_sitl()
          
      def wait_for_ready(self):
          # Wait for all nodes active
          # Wait for vehicle state DISARMED
          # Wait for camera publishing

□ SITL tests:
  
  test_takeoff_land.py:
  - Arm, takeoff, hover, land
  - Verify altitude reached
  - Verify clean landing
  
  test_search_detect.py:
  - Full search mission
  - Verify target found
  - Verify mission completes
  
  test_full_mission.py:
  - Complete ArUco approach mission
  - Verify all phases
  - Verify approach distance

□ Add test result collection:
  - Rosbag recording during test
  - Screenshot on failure
  - Log collection
```

**Expected Output:** Automated SITL tests running

#### Day 7: CI Pipeline Setup (6-8 hrs)

```
□ Create GitHub Actions workflow (.github/workflows/ci.yml):
  
  name: CI Pipeline
  
  on: [push, pull_request]
  
  jobs:
    lint:
      runs-on: ubuntu-22.04
      steps:
        - uses: actions/checkout@v4
        - name: Python lint (ruff)
          run: ruff check src/
        - name: Python format (black)
          run: black --check src/
    
    unit-tests:
      runs-on: ubuntu-22.04
      container: 
        image: osrf/ros:humble-desktop
      steps:
        - uses: actions/checkout@v4
        - name: Install dependencies
          run: |
            apt-get update
            rosdep install --from-paths src -y
        - name: Build
          run: colcon build
        - name: Test
          run: colcon test
        - name: Results
          run: colcon test-result --verbose
    
    integration-tests:
      runs-on: ubuntu-22.04
      container:
        image: ${{ secrets.SITL_IMAGE }}  # Custom SITL image
      steps:
        - name: Run integration tests
          run: pytest test/integration/ --timeout=120

□ Create Docker image for CI:
  - Lighter than dev image
  - Pre-built dependencies
  - Push to GitHub Container Registry

□ Verify CI runs on push
```

**Week 13 Deliverables:**
- [ ] Unit tests with >80% coverage
- [ ] Integration tests passing
- [ ] SITL tests automated
- [ ] CI pipeline running

**Estimated Hours:** 40-45

---

### Week 14: Documentation & Final Polish

**Goal:** Production-ready codebase with documentation

#### Day 1-2: Code Documentation (8-10 hrs)

```
□ Docstrings for all public functions/classes:
  - Google style docstrings
  - Include Args, Returns, Raises
  - Include usage examples for key functions

□ Module-level documentation:
  - Each package has README.md
  - Architecture explanation
  - Usage examples

□ Type hints throughout:
  def compute_velocity(
      self, 
      drone_pose: PoseStamped, 
      target_pose: PoseStamped
  ) -> Tuple[TwistStamped, Dict[str, float]]:
```

**Expected Output:** Well-documented code

#### Day 3-4: User Documentation (10-12 hrs)

```
□ README.md (root):
  - Project overview
  - Quick start guide
  - Architecture diagram
  - Requirements

□ docs/installation.md:
  - Prerequisites
  - Docker setup
  - Native installation (optional)
  - Verification steps

□ docs/running.md:
  - SITL usage
  - Mission execution
  - Monitoring with RViz
  - Troubleshooting

□ docs/development.md:
  - Development environment setup
  - Testing guide
  - Contributing guidelines
  - Code style

□ docs/architecture.md:
  - Layer descriptions
  - Component interactions
  - Design decisions

□ docs/api/: (auto-generated)
  - Sphinx for Python
  - Doxygen for C++ (if any)
```

**Expected Output:** Comprehensive documentation

#### Day 5-6: Portfolio Preparation (8-10 hrs)

```
□ Create demo video:
  - 3-5 minutes
  - Show SITL mission
  - Explain architecture
  - Highlight key features

□ Create technical presentation (5-10 slides):
  - Problem statement
  - Architecture overview
  - Key technical challenges solved
  - Results and metrics
  - Future roadmap

□ Update personal portfolio/GitHub:
  - Professional README with badges
  - Demo GIF
  - Link to video

□ Prepare talking points for interviews:
  - "Tell me about your UAV project"
  - Technical deep-dive questions
  - Design decision justifications
```

**Expected Output:** Portfolio-ready presentation

#### Day 7: Phase 5 Review (4-5 hrs)

```
□ Final CI verification:
  - All tests green
  - Coverage report published
  - Documentation builds

□ Release checklist:
  - Version tagged (v0.5.0)
  - CHANGELOG.md updated
  - Release notes written

□ Handoff preparation:
  - List of known issues
  - Recommended next steps
  - Hardware preparation notes

□ Git tag: v0.5.0-release
```

**Phase 5 Deliverables:**
- [ ] Comprehensive test suite
- [ ] CI pipeline working
- [ ] Full documentation
- [ ] Demo video
- [ ] Portfolio-ready

**Phase 5 Total Hours:** 75-90

---

## Phase 6: Hardware Deployment (Weeks 15-16)

### Week 15: RPi5 Setup & Basic Flight

**Goal:** Nodes running on RPi5, basic manual flight test

#### Day 1-2: RPi5 Environment Setup (10-12 hrs)

```
□ RPi5 base setup:
  - Ubuntu 24.04 Server (64-bit)
  - ROS2 Humble (from source or apt)
  - Required packages

□ Create hardware Docker image:
  - Minimal dependencies
  - Optimized for ARM64
  - Pre-built workspace

□ Network configuration:
  - Static IP for RPi5
  - ROS2 DDS configuration for reliability
  - SSH access configured

□ Serial connection to FC:
  - UART configuration for MAVLINK
  - Test with mavlink-routerd
  - Verify telemetry received
```

**Expected Output:** RPi5 communicates with FC

#### Day 3-4: Camera Integration (8-10 hrs)

```
□ Camera hardware setup:
  - USB camera or RPi Camera Module
  - v4l2 driver verification
  - Test with v4l2-ctl

□ ROS2 camera driver:
  - usb_cam or raspicam_node
  - Verify image publishing
  - Camera info calibration

□ Camera calibration:
  - Checkerboard calibration
  - Save calibration file
  - Verify pose estimation accuracy

□ Verify detector works with real camera:
  - Print ArUco marker
  - Test detection and pose
```

**Expected Output:** Real camera feeding detector

#### Day 5-6: Tethered Testing (8-10 hrs)

```
□ Bench test (drone on bench, props off):
  - Launch all nodes
  - Verify state machine works
  - Verify detection with real camera
  - Verify telemetry from FC

□ Tethered hover test:
  - Drone secured but allowed to lift slightly
  - Test arm/disarm
  - Test brief takeoff
  - Monitor CPU/memory usage

□ Performance optimization:
  - Reduce camera resolution if needed
  - Optimize detection parameters
  - Reduce unnecessary logging

□ Create hardware launch files:
  hardware.launch.py
  - Real camera params
  - Real FCU params
  - Optimized settings
```

**Expected Output:** Tethered test successful

#### Day 7: Week 15 Review (4-5 hrs)

```
□ Hardware checklist:
  - All sensors connected
  - All nodes running
  - No error messages
  - CPU/memory within limits

□ Safety checklist:
  - Kill switch functional
  - Failsafe parameters set
  - Geofence configured (if available)

□ Documentation:
  - Hardware setup guide
  - Pre-flight checklist
  - Emergency procedures

□ Prepare for outdoor testing
```

**Week 15 Deliverables:**
- [ ] RPi5 running all nodes
- [ ] Real camera integrated
- [ ] FC communication verified
- [ ] Tethered test successful

**Estimated Hours:** 35-40

---

### Week 16: Flight Testing

**Goal:** Successful outdoor flight with ArUco mission

#### Day 1-2: Pre-Flight Validation (6-8 hrs)

```
□ HITL testing (if possible):
  - Real FC with simulated physics
  - Verify control loop
  - Verify failsafes trigger correctly

□ Final hardware checks:
  - Propeller balance
  - Motor direction
  - CG (center of gravity)
  - Battery secured

□ Pre-flight software checks:
  - All nodes launch without errors
  - Detection works with printed marker
  - State machine transitions correct
  - Logging working

□ Prepare flight test area:
  - Open area, no obstacles
  - Printed ArUco marker on stand
  - Spotter available
```

**Expected Output:** Ready for first flight

#### Day 3-4: Progressive Flight Testing (10-12 hrs)

```
□ Flight Test 1: Manual Hover
  - Switch to manual/stabilize mode
  - Brief hover (30 seconds)
  - Verify drone is stable
  - Land manually
  - Review logs

□ Flight Test 2: Guided Hover
  - Switch to GUIDED mode (via ROS2)
  - Command position hold
  - Verify position holding
  - Land via ROS2 command
  - Review logs

□ Flight Test 3: Takeoff Action
  - Use ROS2 takeoff action
  - Hover at 2m
  - Land via ROS2
  - Verify all telemetry correct

□ Flight Test 4: Search (No Approach)
  - Takeoff
  - Execute rotate search
  - Verify detection in logs
  - Land

□ Document each flight:
  - Video recording
  - Rosbag recording
  - Notes on any issues
```

**Expected Output:** Progressive flight milestones achieved

#### Day 5-6: Full Mission Testing (8-10 hrs)

```
□ Flight Test 5: Full Mission (Conservative)
  - Slow approach speed (0.1 m/s)
  - Larger target distance (2m)
  - Full mission execution
  - Document results

□ Flight Test 6: Full Mission (Nominal)
  - Normal approach speed (0.3 m/s)
  - Normal target distance (1m)
  - Multiple runs
  - Measure success rate

□ Troubleshoot any issues:
  - Analyze failed runs
  - Adjust parameters
  - Re-test

□ Performance documentation:
  - Mission success rate
  - Approach accuracy
  - Total mission time
  - Any limitations discovered
```

**Expected Output:** Full mission working on real hardware

#### Day 7: Project Wrap-up (4-5 hrs)

```
□ Final documentation:
  - Flight test results
  - Hardware configuration
  - Known limitations
  - Recommended improvements

□ Create final demo video:
  - Real flight footage
  - Overlay with RViz data
  - Narration explaining system

□ Update portfolio:
  - Add real flight video
  - Update README with results
  - Add flight photos

□ Future roadmap document:
  - YOLO integration
  - Moving target tracking
  - Multi-drone coordination
  - Path planning

□ Git tag: v1.0.0
```

**Phase 6 Deliverables:**
- [ ] Hardware deployment complete
- [ ] Progressive flight testing done
- [ ] Full mission on real hardware
- [ ] Final documentation
- [ ] Portfolio updated with real results

**Phase 6 Total Hours:** 75-90

---

## Project Summary

### Total Estimated Hours

| Phase | Hours | Cumulative |
|-------|-------|------------|
| Phase 1: Foundation | 100-120 | 100-120 |
| Phase 2: Perception | 100-120 | 200-240 |
| Phase 3: Simple Mission | 100-120 | 300-360 |
| Phase 4: Visual Servoing | 100-120 | 400-480 |
| Phase 5: Integration & CI | 75-90 | 475-570 |
| Phase 6: Hardware | 75-90 | 550-660 |

**Total: 550-660 hours over 16 weeks (35-40 hrs/week)**

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Gazebo Harmonic issues | Have Gazebo Classic as backup |
| MAVROS integration problems | Budget extra time in Phase 1 |
| Visual servoing tuning | Conservative initial params, lots of SITL testing |
| Hardware delays | Order parts in Week 1, have backup suppliers |
| RPi5 performance | Have Jetson Orin Nano as backup for YOLO |

### Success Metrics

By Week 16, you should be able to demonstrate:

1. **SITL:** 95%+ mission success rate
2. **Hardware:** Successful outdoor ArUco mission
3. **Portfolio:** Professional documentation and video
4. **Skills:** ROS2, BT, visual servoing, real flight ops

---

*This roadmap is a living document. Update weekly with actual progress, lessons learned, and adjustments.*
