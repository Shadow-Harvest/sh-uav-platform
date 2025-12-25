# Autonomous UAV Platform Architecture

## Executive Summary

Enterprise-grade autonomous UAV platform built on ROS2, designed for defense/aerospace standards (NASA, DARPA, Anduril, Tesla). Simulation-first approach with seamless SITL → HITL → Hardware deployment path.

---

## 1. Architectural Principles

### 1.1 Core Design Philosophy

```
┌─────────────────────────────────────────────────────────────────┐
│                    DESIGN PRINCIPLES                            │
├─────────────────────────────────────────────────────────────────┤
│  • Separation of Concerns    - Each layer has ONE responsibility│
│  • Dependency Inversion      - Depend on abstractions, not impl │
│  • Configuration over Code   - Swap components via YAML/params  │
│  • Fail-Safe by Default      - Every component assumes failure  │
│  • Simulation Parity         - Same code runs in SITL & hardware│
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 When to Use State Machines vs Behavior Trees

| Aspect | Finite State Machine (FSM) | Behavior Tree (BT) |
|--------|---------------------------|-------------------|
| **Use For** | Vehicle lifecycle, safety states, mode transitions | Mission logic, task sequencing, reactive behaviors |
| **Characteristics** | Deterministic, verifiable, linear | Composable, hierarchical, reactive |
| **Examples** | DISARMED→ARMED→FLYING→LANDED | Search→Detect→Approach→Land |
| **Verification** | Formal methods possible | Runtime monitoring |
| **Complexity** | O(states × transitions) | O(tree depth) |

**Architecture Decision**: FSM manages WHAT the vehicle CAN do (safety envelope). BT decides WHAT it SHOULD do (mission logic).

### 1.3 ArduPilot GUIDED Mode Behavior

**Critical Understanding**: ArduPilot operates with a two-layer control model:

```
┌─────────────────────────────────────────────┐
│   FLIGHT PHASE CONTROL (Native Commands)   │
│   - Takeoff (NAV_TAKEOFF)                   │
│   - Land (NAV_LAND)                         │
│   - ArduPilot handles these INTERNALLY      │
│   - After takeoff: GUIDED Loiter (auto-hold)│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   POSITION CONTROL (Setpoint Streaming)     │
│   - ONLY for active movement while airborne │
│   - NOT required to maintain position       │
│   - ArduPilot holds autonomously in GUIDED  │
└─────────────────────────────────────────────┘
```

**Key Principles**:
- **NAV_TAKEOFF required**: Position setpoints alone cannot initiate takeoff
- **Autonomous hold**: After NAV_TAKEOFF completes, ArduPilot enters GUIDED Loiter and holds position without continuous setpoints
- **Failsafe behavior**: Only triggers on GCS heartbeat loss, NOT on setpoint loss
- **Setpoints for movement**: Position/velocity setpoints only needed when actively moving to new positions

---

## 2. System Architecture

### 2.1 Layered Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MISSION LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Behavior Tree Engine (py_trees)                     │   │
│  │   [Sequence: Takeoff → Search → Approach → Hold → Land]         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                        PLANNING LAYER                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐   │
│  │  Path Planner    │  │ Approach Planner │  │ Search Pattern Gen │   │
│  │  (future: A*)    │  │ (visual servo)   │  │ (spiral/sweep)     │   │
│  └──────────────────┘  └──────────────────┘  └────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                      WORLD MODEL LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    State Estimator Node                          │   │
│  │  • Vehicle State (pose, velocity, battery, health)              │   │
│  │  • Target State (detected targets, confidence, tracking)        │   │
│  │  • Environment (obstacles future)                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                      PERCEPTION LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              Target Detector Node (Abstract Interface)           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │   ArUco     │  │    YOLO     │  │   Future Detectors...   │  │   │
│  │  │  Plugin     │  │   Plugin    │  │   (AprilTag, Custom)    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                       CONTROL LAYER                                     │
│  ┌──────────────────────────────┐  ┌────────────────────────────────┐ │
│  │     Vehicle Controller       │  │      Safety Monitor            │ │
│  │  • Flight phase commands     │  │  • Geofence enforcement        │ │
│  │  •   (Takeoff/Land via       │  │  • Battery watchdog            │ │
│  │  •    MAVROS services)       │  │  • Failsafe triggers           │ │
│  │  • Position/Velocity setpts  │  │  • State monitoring            │ │
│  │  •   (only for movement)     │  │                                │ │
│  └──────────────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                    VEHICLE STATE MACHINE                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        FSM (Safety Layer)                        │   │
│  │                                                                   │   │
│  │    ┌──────────┐     arm      ┌────────┐     takeoff  ┌────────┐ │   │
│  │    │DISARMED  │─────────────▶│ ARMED  │─────────────▶│ FLYING │ │   │
│  │    └──────────┘              └────────┘              └────────┘ │   │
│  │          ▲                        │                      │  │    │   │
│  │          │         disarm         │                      │  │    │   │
│  │          └────────────────────────┘                land  │  │    │   │
│  │          ▲                                               │  │    │   │
│  │          │                      ┌────────┐               │  │    │   │
│  │          └──────────────────────│ LANDED │◀──────────────┘  │    │   │
│  │                                 └────────┘                   │    │   │
│  │                                      ▲        emergency      │    │   │
│  │                                      │     ┌───────────┐     │    │   │
│  │                                      └─────│ EMERGENCY │◀────┘    │   │
│  │                                            └───────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│                 HARDWARE ABSTRACTION LAYER (HAL)                        │
│  ┌──────────────────────────┐  ┌────────────────────────────────────┐ │
│  │      MAVROS Interface    │  │       Camera Interface             │ │
│  │  • Telemetry subscriber  │  │  • image_transport                 │ │
│  │  • Command publisher     │  │  • Camera info                     │ │
│  │  • Service proxies       │  │  • Sim/Real camera abstraction     │ │
│  └──────────────────────────┘  └────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────────┐
              │  SITL    │   │  HITL    │   │  Hardware    │
              │ Gazebo   │   │  FC+Sim  │   │  RPi5 + FC   │
              └──────────┘   └──────────┘   └──────────────┘
```

---

## 3. Component Specifications

### 3.1 ROS2 Node Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ROS2 NODE TOPOLOGY                              │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   mission_executor  │ ←── BehaviorTree runtime
                    │   (Lifecycle Node)  │
                    └─────────┬───────────┘
                              │ /mission/status
                              │ /mission/command
                    ┌─────────▼───────────┐
                    │   state_estimator   │ ←── World model fusion
                    │   (Lifecycle Node)  │
                    └─────────┬───────────┘
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │ target_detector │ │vehicle_controller│ │ safety_monitor  │
  │ (Lifecycle Node)│ │ (Lifecycle Node) │ │ (Lifecycle Node)│
  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
           │                   │                   │
           │/detection/targets │/control/setpoint  │/safety/status
           │                   │                   │
  ┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
  │  camera_driver  │ │     mavros      │ │  (monitors all) │
  │   (external)    │ │   (external)    │ │                 │
  └─────────────────┘ └─────────────────┘ └─────────────────┘
           │                   │
           ▼                   ▼
    ┌────────────┐      ┌────────────┐
    │  Gazebo /  │      │ ArduPilot  │
    │  Real Cam  │      │ SITL/Real  │
    └────────────┘      └────────────┘
```

### 3.2 Core Interfaces (ROS2 Messages/Services/Actions)

```yaml
# Custom message definitions

# --- Detection Interface (Perception Layer) ---
autonomous_uav_msgs/msg/DetectedTarget:
  std_msgs/Header header
  string target_id                    # Unique identifier (e.g., "aruco_42")
  string target_class                 # "aruco", "yolo_person", "apriltag"
  geometry_msgs/PoseStamped pose      # 3D pose in camera frame
  float32 confidence                  # 0.0 - 1.0
  float32[4] bounding_box             # [x, y, width, height] normalized

autonomous_uav_msgs/msg/DetectedTargetArray:
  std_msgs/Header header
  DetectedTarget[] targets

# --- Vehicle State (World Model Layer) ---
autonomous_uav_msgs/msg/VehicleState:
  std_msgs/Header header
  uint8 flight_state                  # FSM state enum
  geometry_msgs/PoseStamped pose
  geometry_msgs/TwistStamped velocity
  float32 battery_percentage
  bool is_armed
  bool is_offboard
  string[] active_faults

# --- Mission Interface ---
autonomous_uav_msgs/action/ExecuteMission:
  # Goal
  string mission_id
  string behavior_tree_xml            # Or path to XML file
  ---
  # Result
  bool success
  string result_message
  ---
  # Feedback
  string current_behavior
  float32 progress_percentage
  VehicleState vehicle_state
```

---

## 4. Perception Layer: Plugin Architecture

### 4.1 Detector Plugin System

```
┌─────────────────────────────────────────────────────────────────┐
│                 PERCEPTION PLUGIN ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

                    ┌───────────────────────┐
                    │   target_detector     │
                    │      (ROS2 Node)      │
                    └───────────┬───────────┘
                                │ loads via pluginlib
                    ┌───────────▼───────────┐
                    │  DetectorPluginBase   │ ←── Abstract Interface
                    │  (Pure Virtual Class) │
                    └───────────┬───────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  ArUcoDetector  │   │  YOLODetector   │   │ AprilTagDetector│
│    Plugin       │   │    Plugin       │   │     Plugin      │
├─────────────────┤   ├─────────────────┤   ├─────────────────┤
│• OpenCV ArUco   │   │• ONNX Runtime   │   │• apriltag lib   │
│• Dictionary cfg │   │• Model path cfg │   │• Family config  │
│• Detection params│  │• Confidence thr │   │• Detection cfg  │
└─────────────────┘   └─────────────────┘   └─────────────────┘

# Configuration-driven selection (params.yaml)
target_detector:
  ros__parameters:
    plugin_name: "aruco_detector"  # Change to "yolo_detector" etc.
    
    aruco_detector:
      dictionary: "DICT_4X4_50"
      marker_size_m: 0.15
      
    yolo_detector:
      model_path: "/models/yolov8n.onnx"
      confidence_threshold: 0.7
      target_classes: ["person", "car"]
```

### 4.2 Detector Base Interface

```cpp
// detector_plugin_base.hpp (C++ for performance, Python bindings available)
class DetectorPluginBase {
public:
    virtual ~DetectorPluginBase() = default;
    
    // Lifecycle
    virtual void initialize(const rclcpp::Node::SharedPtr& node) = 0;
    virtual void configure(const YAML::Node& config) = 0;
    
    // Core detection interface
    virtual DetectedTargetArray detect(
        const sensor_msgs::msg::Image& image,
        const sensor_msgs::msg::CameraInfo& camera_info
    ) = 0;
    
    // Introspection
    virtual std::string getPluginName() const = 0;
    virtual std::vector<std::string> getSupportedTargetClasses() const = 0;
};
```

---

## 5. Mission Layer: Behavior Tree Design

### 5.1 First Mission: ArUco Search & Approach

```
┌─────────────────────────────────────────────────────────────────┐
│              BEHAVIOR TREE: ArUco Search & Approach             │
└─────────────────────────────────────────────────────────────────┘

                              [Root]
                                │
                          ┌─────▼─────┐
                          │ Sequence  │
                          └─────┬─────┘
                                │
        ┌───────────┬───────────┼───────────┐
        │           │           │           │
        ▼           ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Takeoff │ │ Search  │ │Approach │ │  Land   │
   │ Action  │ │Fallback │ │ Action  │ │ Action  │
   └─────────┘ └────┬────┘ └─────────┘ └─────────┘
                    │
        ┌───────────▼───────────┐
        │       Fallback        │
        └───────────┬───────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
    ┌───────────┐       ┌───────────┐
    │  Target   │       │  Rotate   │
    │ Visible?  │       │  Search   │
    │(Condition)│       │ (Action)  │
    └───────────┘       └───────────┘
                              │
                    ┌─────────▼─────────┐
                    │     Sequence      │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              ┌───────────┐       ┌───────────┐
              │   Yaw     │       │  Check    │
              │  +30 deg  │       │ Detection │
              │ (Action)  │       │(Condition)│
              └───────────┘       └───────────┘
```

### 5.2 BT XML Definition

```xml
<!-- mission_aruco_approach.xml -->
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence name="aruco_search_approach">

      <!-- Pre-conditions -->
      <Condition ID="IsArmed"/>

      <!-- Takeoff to search altitude -->
      <Action ID="Takeoff" altitude="3.0" timeout_sec="30"/>

      <!-- Search Pattern with Fallback -->
      <Fallback name="search_fallback">
        <Condition ID="TargetDetected" target_class="aruco"/>
        <Action ID="RotateSearch"
                yaw_step_deg="30"
                pause_sec="2.0"
                max_rotations="12"/>
      </Fallback>

      <!-- Approach Target -->
      <Action ID="ApproachTarget"
              target_distance_m="0.5"
              approach_speed="0.3"
              timeout_sec="60"/>

      <!-- Wait at Target (ArduPilot holds position autonomously) -->
      <Action ID="Wait" duration_sec="10"/>

      <!-- Land -->
      <Action ID="Land" timeout_sec="30"/>

    </Sequence>
  </BehaviorTree>
</root>
```

### 5.3 BT Node Implementations (py_trees)

```python
# Behavior tree nodes map directly to ROS2 actions/services

class TakeoffAction(py_trees_ros.actions.ActionClient):
    """
    Calls /mavros/cmd/takeoff service (NAV_TAKEOFF command).
    After completion, ArduPilot automatically holds position in GUIDED Loiter mode.
    """

class RotateSearchAction(py_trees.behaviour.Behaviour):
    """
    Rotates vehicle incrementally until target detected.
    - Subscribes: /detection/targets
    - Commands: Yaw changes via vehicle controller
    - Blackboard: writes detected_target when found
    Note: ArduPilot holds altitude autonomously during rotation
    """

class ApproachTargetAction(py_trees.behaviour.Behaviour):
    """
    Visual servoing approach to target.
    - Reads: detected_target from blackboard
    - Implements: proportional approach controller
    - Stops at: target_distance_m
    - Uses: Position/velocity setpoints for active movement
    """

class WaitAction(py_trees.behaviour.Behaviour):
    """
    Simple time-based wait.
    Vehicle holds position autonomously via ArduPilot GUIDED Loiter.
    No active setpoint streaming required.
    """
```

---

## 6. Vehicle State Machine (Safety FSM)

### 6.1 State Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│                    VEHICLE STATE MACHINE                        │
│                   (Safety-Critical FSM)                         │
└─────────────────────────────────────────────────────────────────┘

States:
┌────────────────┬────────────────────────────────────────────────┐
│ UNINITIALIZED  │ System startup, awaiting connections          │
├────────────────┼────────────────────────────────────────────────┤
│ DISARMED       │ Safe state, motors off, accepts commands      │
├────────────────┼────────────────────────────────────────────────┤
│ ARMING         │ Transition state, pre-arm checks running      │
├────────────────┼────────────────────────────────────────────────┤
│ ARMED          │ Motors ready, awaiting takeoff command        │
├────────────────┼────────────────────────────────────────────────┤
│ TAKING_OFF     │ Ascending to target altitude                  │
├────────────────┼────────────────────────────────────────────────┤
│ FLYING         │ Nominal flight, mission active                │
├────────────────┼────────────────────────────────────────────────┤
│ LANDING        │ Controlled descent                            │
├────────────────┼────────────────────────────────────────────────┤
│ LANDED         │ On ground, still armed                        │
├────────────────┼────────────────────────────────────────────────┤
│ EMERGENCY      │ Failsafe triggered, autonomous recovery       │
├────────────────┼────────────────────────────────────────────────┤
│ FAULT          │ Unrecoverable error, requires intervention    │
└────────────────┴────────────────────────────────────────────────┘

Transitions:
┌─────────────────────────────────────────────────────────────────┐
│ Transition          │ Guard Conditions                         │
├─────────────────────┼───────────────────────────────────────────┤
│ DISARMED → ARMING   │ arm_command && pre_arm_checks_pass       │
│ ARMING → ARMED      │ arming_complete && no_faults             │
│ ARMED → TAKING_OFF  │ takeoff_command && altitude_valid        │
│ TAKING_OFF → FLYING │ altitude_reached                         │
│ FLYING → LANDING    │ land_command || mission_complete         │
│ LANDING → LANDED    │ ground_contact && velocity_zero          │
│ LANDED → DISARMED   │ disarm_command                           │
│ * → EMERGENCY       │ critical_fault || manual_emergency       │
│ EMERGENCY → LANDED  │ safe_landing_complete                    │
└─────────────────────┴───────────────────────────────────────────┘
```

### 6.2 FSM Implementation Pattern

```python
# Using python-statemachine for FSM
from statemachine import StateMachine, State

class VehicleStateMachine(StateMachine):
    """Safety-critical vehicle state machine."""
    
    # States
    uninitialized = State(initial=True)
    disarmed = State()
    arming = State()
    armed = State()
    taking_off = State()
    flying = State()
    landing = State()
    landed = State()
    emergency = State()
    
    # Transitions (with guards)
    initialize = uninitialized.to(disarmed)
    arm = disarmed.to(arming, cond="pre_arm_checks_pass")
    arm_complete = arming.to(armed)
    takeoff = armed.to(taking_off, cond="altitude_valid")
    reached_altitude = taking_off.to(flying)
    land = flying.to(landing)
    touched_down = landing.to(landed)
    disarm = landed.to(disarmed)
    
    # Emergency transitions from any state
    emergency_trigger = (
        armed.to(emergency) |
        taking_off.to(emergency) |
        flying.to(emergency) |
        landing.to(emergency)
    )
    
    # Guards
    def pre_arm_checks_pass(self) -> bool:
        return (
            self.vehicle.battery_ok and
            self.vehicle.gps_ok and
            self.vehicle.ekf_ok and
            not self.vehicle.has_faults
        )
```

---

## 7. Data Flow Architecture

### 7.1 Topic Structure

```yaml
# Namespaced topic organization

/mavros/                          # HAL - Flight controller interface
  state                           # Vehicle arm/mode status
  local_position/pose             # Fused position estimate
  local_position/velocity_local   # Velocity
  setpoint_position/local         # Position commands
  setpoint_velocity/cmd_vel       # Velocity commands
  cmd/arming                      # Arm/disarm service
  set_mode                        # Flight mode service

/camera/                          # HAL - Vision interface
  image_raw                       # Raw camera images
  camera_info                     # Intrinsics for pose estimation

/detection/                       # Perception layer outputs
  targets                         # DetectedTargetArray
  debug_image                     # Visualization (optional)

/vehicle/                         # World model / state
  state                           # VehicleState (fused)
  target_state                    # Tracked target info

/control/                         # Control layer
  setpoint                        # Commanded setpoint
  status                          # Controller status

/mission/                         # Mission layer
  status                          # Mission execution status
  command                         # Mission commands (start/stop/pause)

/safety/                          # Safety monitor
  status                          # Safety system status
  faults                          # Active fault list
```

### 7.2 QoS Profiles

```yaml
# Quality of Service configuration by data type

qos_profiles:
  telemetry:           # High-rate sensor data
    reliability: BEST_EFFORT
    durability: VOLATILE
    history_depth: 1
    
  state:               # Vehicle/mission state
    reliability: RELIABLE
    durability: TRANSIENT_LOCAL
    history_depth: 1
    
  command:             # Control commands
    reliability: RELIABLE
    durability: VOLATILE
    history_depth: 5
    
  detection:           # Detection results
    reliability: BEST_EFFORT
    durability: VOLATILE
    history_depth: 1
```

---

## 8. Package Structure

```
autonomous_uav/
├── autonomous_uav_bringup/        # Launch files, configs
│   ├── launch/
│   │   ├── sitl.launch.py         # Full SITL simulation
│   │   ├── hitl.launch.py         # Hardware-in-the-loop
│   │   ├── hardware.launch.py     # Real hardware
│   │   └── components/            # Composable launches
│   ├── config/
│   │   ├── sitl/                  # SITL-specific params
│   │   ├── hardware/              # Hardware-specific params
│   │   └── common/                # Shared params
│   └── worlds/                    # Gazebo world files
│
├── autonomous_uav_msgs/           # Custom interfaces
│   ├── msg/
│   ├── srv/
│   └── action/
│
├── autonomous_uav_perception/     # Perception layer
│   ├── include/                   # C++ headers
│   ├── src/
│   │   ├── target_detector_node.cpp
│   │   └── plugins/
│   │       ├── aruco_detector.cpp
│   │       └── yolo_detector.cpp
│   ├── autonomous_uav_perception/ # Python package
│   │   └── ...
│   └── test/
│
├── autonomous_uav_control/        # Control layer
│   ├── autonomous_uav_control/
│   │   ├── vehicle_controller.py
│   │   ├── safety_monitor.py
│   │   └── vehicle_fsm.py
│   └── test/
│
├── autonomous_uav_planning/       # Planning layer
│   ├── autonomous_uav_planning/
│   │   ├── approach_planner.py
│   │   └── search_patterns.py
│   └── test/
│
├── autonomous_uav_mission/        # Mission layer
│   ├── autonomous_uav_mission/
│   │   ├── mission_executor.py
│   │   └── behaviors/             # BT nodes
│   │       ├── takeoff.py
│   │       ├── rotate_search.py
│   │       ├── approach_target.py
│   │       └── conditions.py
│   ├── trees/                     # BT XML definitions
│   │   └── aruco_approach.xml
│   └── test/
│
├── autonomous_uav_state/          # World model layer
│   ├── autonomous_uav_state/
│   │   └── state_estimator.py
│   └── test/
│
├── autonomous_uav_simulation/     # Simulation assets
│   ├── models/                    # Gazebo models
│   ├── worlds/                    # Gazebo worlds
│   └── plugins/                   # Gazebo plugins
│
└── docker/                        # Containerization
    ├── Dockerfile.sitl            # SITL development
    ├── Dockerfile.hardware        # Hardware deployment
    └── docker-compose.yml
```

---

## 9. Testing Strategy

### 9.1 Testing Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  ← Full mission SITL tests
                    │   Tests     │    (GitHub Actions, nightly)
                    ├─────────────┤
                    │ Integration │  ← Multi-node ROS2 tests
                    │   Tests     │    (launch_testing)
                    ├─────────────┤
                    │    Unit     │  ← Component logic
                    │   Tests     │    (pytest, gtest)
                    └─────────────┘
                         Base
```

### 9.2 Test Categories

```yaml
unit_tests:
  - FSM transition logic
  - Detection algorithms (mocked images)
  - Path/approach planners (geometric calculations)
  - BT node individual behavior
  coverage_target: 80%
  
integration_tests:
  - Perception pipeline (camera → detection → state)
  - Control pipeline (setpoint → MAVROS → response)
  - Mission executor (BT → behaviors → control)
  tools: [launch_testing, pytest-ros]
  
sitl_tests:
  - Complete missions in Gazebo
  - Fault injection scenarios
  - Performance benchmarks
  ci_frequency: "every PR"
  
hitl_tests:
  - Pre-flight validation suite
  - Sensor health checks
  - Communication latency tests
  when: "before each flight"
```

### 9.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - name: Python lint (ruff)
      - name: C++ lint (clang-format)
      - name: ROS2 lint (ament_lint)
      
  unit-tests:
    runs-on: ubuntu-22.04
    container: autonomous_uav:sitl
    steps:
      - name: Build workspace
      - name: Run unit tests
      - name: Upload coverage
      
  integration-tests:
    runs-on: ubuntu-22.04
    container: autonomous_uav:sitl
    steps:
      - name: Build workspace
      - name: Run integration tests (launch_testing)
      
  sitl-tests:
    runs-on: ubuntu-22.04
    container: autonomous_uav:sitl
    steps:
      - name: Start SITL + Gazebo
      - name: Run mission tests
      - name: Archive logs on failure
```

---

## 10. Deployment Modes

### 10.1 Environment Configurations

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT MODES                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│      SITL       │  │      HITL       │  │    HARDWARE     │
│  (Development)  │  │   (Validation)  │  │  (Production)   │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│                 │  │                 │  │                 │
│  Dev Machine    │  │  Dev Machine    │  │  Raspberry Pi 5 │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │ Gazebo    │  │  │  │ Gazebo    │  │  │  │ ROS2 Nodes│  │
│  │ (Physics) │  │  │  │ (Visuals) │  │  │  │           │  │
│  └─────┬─────┘  │  │  └───────────┘  │  │  └─────┬─────┘  │
│        │        │  │                 │  │        │        │
│  ┌─────▼─────┐  │  │  ┌───────────┐  │  │  ┌─────▼─────┐  │
│  │ ArduPilot │  │  │  │ ArduPilot │  │  │  │  MAVROS   │  │
│  │   SITL    │  │  │  │   SITL    │◄─┼──┼──│           │  │
│  └─────┬─────┘  │  │  └─────┬─────┘  │  │  └─────┬─────┘  │
│        │        │  │        │ HIL    │  │        │ Serial │
│  ┌─────▼─────┐  │  │  ┌─────▼─────┐  │  │  ┌─────▼─────┐  │
│  │  MAVROS   │  │  │  │   Real    │  │  │  │   Real    │  │
│  │           │  │  │  │    FC     │  │  │  │    FC     │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
│                 │  │                 │  │                 │
│  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │
│  │ ROS2 Nodes│  │  │  │ ROS2 Nodes│  │  │  │Real Camera│  │
│  │           │  │  │  │           │  │  │  │           │  │
│  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │
└─────────────────┘  └─────────────────┘  └─────────────────┘

Same ROS2 code        Same ROS2 code        Same ROS2 code
Config: sitl.yaml     Config: hitl.yaml     Config: hw.yaml
```

### 10.2 Configuration Management

```yaml
# config/common/perception.yaml (shared)
target_detector:
  ros__parameters:
    plugin_name: "aruco_detector"
    publish_debug_image: true
    aruco_detector:
      dictionary: "DICT_4X4_50"
      marker_size_m: 0.15

# config/sitl/perception.yaml (overrides)
target_detector:
  ros__parameters:
    camera_topic: "/gazebo/camera/image_raw"
    camera_info_topic: "/gazebo/camera/camera_info"

# config/hardware/perception.yaml (overrides)  
target_detector:
  ros__parameters:
    camera_topic: "/camera/image_raw"
    camera_info_topic: "/camera/camera_info"
```

---

## 11. Key Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **FSM vs BT** | Both (FSM for safety, BT for mission) | FSM guarantees safety invariants; BT enables complex mission logic |
| **Perception plugins** | pluginlib (C++) / entry_points (Python) | Hot-swappable detectors without recompilation |
| **Lifecycle nodes** | Yes, for all core nodes | Deterministic startup, graceful shutdown, state management |
| **Language** | Python primary, C++ for performance-critical | Rapid iteration for mission logic; C++ for detection/control |
| **Testing** | pytest + launch_testing + SITL | Full coverage from unit to system level |
| **Configuration** | YAML params, launch arguments | Environment-specific without code changes |

---

## 12. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Docker SITL environment setup
- [ ] Basic package structure
- [ ] MAVROS integration verified
- [ ] Vehicle FSM implementation
- [ ] Basic vehicle controller (takeoff/land/hold)

### Phase 2: Perception (Week 3-4)
- [ ] Camera pipeline (sim + real)
- [ ] Detector plugin architecture
- [ ] ArUco detector implementation
- [ ] State estimator with target tracking

### Phase 3: Mission (Week 5-6)
- [ ] BT framework integration (py_trees)
- [ ] Basic behaviors (takeoff, land, hold)
- [ ] Rotate search behavior
- [ ] Approach behavior (visual servoing)

### Phase 4: Integration (Week 7-8)
- [ ] Full mission integration
- [ ] CI/CD pipeline
- [ ] SITL test suite
- [ ] Documentation

### Phase 5: Hardware (Week 9-10)
- [ ] RPi5 deployment
- [ ] Real camera integration
- [ ] HITL testing
- [ ] First real flight

---

## Appendix A: Technology Stack Reference

| Component | Technology | Version |
|-----------|------------|---------|
| OS | Ubuntu 22.04 LTS | Jammy |
| ROS | ROS2 Humble | LTS |
| Simulator | Gazebo Harmonic | Latest |
| Flight Stack | ArduPilot | 4.5.x |
| ROS-FC Bridge | MAVROS | 2.x |
| Behavior Trees | py_trees / py_trees_ros | 2.x |
| State Machine | python-statemachine | 2.x |
| Computer Vision | OpenCV | 4.x |
| ML Inference | ONNX Runtime | 1.x |
| Containerization | Docker | 24.x |
| CI/CD | GitHub Actions | - |

---

*Document Version: 1.0*
*Architecture Status: Design Phase*
