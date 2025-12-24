# Learning Log: Vehicle Controller & Takeoff Action

**Date:** 2025-12-12

**Session:** Week 3 Day 1-2 - Vehicle Controller Implementation

**Duration:** ~3 hours

**Status:** 🟡 In Progress - Core working, callback issue to fix

---

## 🎯 Session Objectives

1. ✅ Created `VehicleController` lifecycle node
2. ✅ Implemented 20Hz setpoint streaming
3. ✅ Built Takeoff action server
4. ✅ Integrated MAVROS service calls (arm, set_mode, takeoff)
5. 🟡 Monitoring loop needs callback fix

---

## 📚 Key Concepts Learned

### 1. Lifecycle Node Pattern

VehicleController follows the lifecycle pattern:
- `on_configure`: Setup subscribers, publishers, service clients, action servers
- `on_activate`: Start timers (20Hz setpoint streaming)
- `on_deactivate`: Stop timers
- `on_cleanup`: Release resources

### 2. Setpoint Streaming (20Hz Heartbeat)

ArduPilot GUIDED mode requires continuous setpoints:
- Must publish >2Hz or drone triggers failsafe
- We use 20Hz (0.05s timer) for smooth control
- This is a "dead man's switch" - proves the controller is alive

```python
self.setpoint_timer = self.create_timer(0.05, self._publish_setpoint)

3. ROS2 Service Calls (Async Pattern)
# 1. Wait for service
if not self.client.wait_for_service(timeout_sec=5.0):
    return False

# 2. Create request
request = ServiceType.Request()
request.field = value

# 3. Call async and wait
future = self.client.call_async(request)
rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

# 4. Check result
if future.result() is not None:
    return future.result().success

Key insight: spin_until_future_complete() blocks the executor. Use MultiThreadedExecutor to keep timers running during service calls.
4. QoS Compatibility
MAVROS uses "sensor data" QoS profile. Must match in subscribers:
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=10
)

self.pose_sub = self.create_subscription(
    PoseStamped,
    '/mavros/local_position/pose',
    self._pose_callback,
    sensor_qos  # NOT just "10"
)

5. ArduPilot Takeoff Sequence
Position setpoints alone don't initiate takeoff. Need MAVROS command:
1. Set GUIDED mode    → /mavros/set_mode
2. Arm                → /mavros/cmd/arming  
3. Takeoff command    → /mavros/cmd/takeoff  ← Actually lifts drone
4. Monitor altitude   → Setpoints maintain position after

6. MultiThreadedExecutor
Required when action callbacks need timers to keep running:
from rclpy.executors import MultiThreadedExecutor

executor = MultiThreadedExecutor()
executor.add_node(node)
executor.spin()

🏗️ What Was Built
VehicleController Node
vehicle_controller.py
├── Lifecycle callbacks (configure, activate, deactivate, cleanup)
├── 20Hz setpoint streaming (_publish_setpoint)
├── Pose subscription with QoS (_pose_callback)
├── MAVROS service clients (arm, set_mode, takeoff)
├── Takeoff action server (_execute_takeoff)
└── Helper methods (_arm_vehicle, _set_mode, _mavros_takeoff, set_target_position)

Takeoff Action Flow
_execute_takeoff()
    │
    ├─► _set_mode('GUIDED')     → MAVROS service call
    │
    ├─► _arm_vehicle(True)      → MAVROS service call
    │
    ├─► _mavros_takeoff(alt)    → MAVROS service call (lifts drone)
    │
    ├─► set_target_position()   → Update setpoint target
    │
    └─► Monitoring loop         → Check altitude, publish feedback
            │
            └─► 🔴 ISSUE: Callbacks not processed during loop

🐛 Known Issue: Callback Processing in Action Loop
Symptom
Drone takes off successfully (visible in Gazebo)
Altitude monitoring shows 0.0 during flight
After timeout/abort, altitude suddenly shows correct value (~10m)
Cause
The while rclpy.ok() loop with time.sleep() doesn't yield to the executor. Pose callbacks are queued but not delivered until action completes.
Solution (TODO)
Replace time.sleep(0.1) with executor spin:
# Instead of:
time.sleep(0.1)

# Use:
for _ in range(10):
    rclpy.spin_once(self, timeout_sec=0.01)

This allows ROS2 to process pending callbacks (pose updates) during the loop.
🔧 Commands Reference
# Build
colcon build --packages-select uav_control --symlink-install
source install/setup.bash

# Run controller
ros2 run uav_control vehicle_controller

# Lifecycle commands
ros2 lifecycle set /vehicle_controller configure
ros2 lifecycle set /vehicle_controller activate

# Send takeoff
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"

# Debug
ros2 topic echo /mavros/local_position/pose --once
ros2 topic hz /mavros/setpoint_position/local
ros2 action list

🚀 What's Next
Immediate (Next Session)
Fix callback processing in takeoff monitoring loop
Test complete takeoff → hover → detect success
Add Land action server
Add HoldPosition action server
Week 3 Remaining
Integration testing with full flight cycle
Error handling improvements
Unit tests for controller
📊 Session Stats
Files created: 1 (vehicle_controller.py)
Files modified: 1 (setup.py entry point)
Concepts learned: 6 major concepts
Bugs encountered: 4 (indentation, QoS, executor, callback processing)
Bugs fixed: 3
Bugs remaining: 1 (callback processing)
💡 Key Insights
Docker networking matters - All ROS2 nodes must be in same container
QoS mismatches are silent - No error, just no data
Lifecycle services can hang - Environment issues cause silent failures
Action callbacks need care - Blocking loops prevent other callbacks
ArduPilot has safety timeouts - Must send commands quickly after arming
✅ Self-Assessment
Can I now:
✅ Create a Lifecycle node? YES
✅ Implement 20Hz setpoint streaming? YES
✅ Call MAVROS services from Python? YES
✅ Create an action server? YES
✅ Handle QoS compatibility? YES
🟡 Process callbacks during action execution? NEEDS WORK
Confidence level: 7/10 - Core concepts solid, need to fix callback issue
Achievement unlocked: 🚁 First Autonomous Takeoff
Session vibe: "It's a mess but the drone flew!"
📝 Environment Notes
SITL Launch Sequence (4 Terminals)
# Terminal 1: Gazebo
make gazebo

# Terminal 2: ArduPilot SITL  
make sitl

# Terminal 3: MAVROS (must exec into same container as controller)
docker exec -it <container> bash
source /opt/ros/humble/setup.bash
ros2 launch mavros apm.launch fcu_url:=udp://:14550@

# Terminal 4: Controller
docker exec -it <container> bash
source /opt/ros/humble/setup.bash
source /ws/install/setup.bash
ros2 run uav_control vehicle_controller

Common Issues Encountered
Issue	Cause	Fix
Lifecycle commands silent	Different containers	Use docker exec into same container
"QoS incompatible" warning	QoS mismatch	Use BEST_EFFORT reliability
Drone disarms after arming	No setpoints during service calls	MultiThreadedExecutor
Altitude shows 0.0	Callbacks not processed	spin_once in loop (TODO)
Status: Day 1-2 substantial progress! One bug to fix, then ready for Land/Hold actions.