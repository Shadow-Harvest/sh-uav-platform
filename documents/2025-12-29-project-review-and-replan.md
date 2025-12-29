# Project Review & Refreshed Plan

**Date:** 2025-12-29
**Reviewer:** Claude (Opus 4.5)
**Status:** Comprehensive Analysis Complete

---

## Executive Summary

This document provides a thorough analysis of the SH-UAV-Platform project, separating **verified facts** (from code) from **aspirational documentation** (learning logs may contain hallucinations). The goal is to establish ground truth and create a precise, realistic plan forward.

---

## Part 1: Ground Truth Analysis (What Actually Exists)

### 1.1 Package Structure (Verified)

```
src/
├── uav_msgs/                 # ✅ EXISTS - Complete
│   ├── msg/                  # 6 message definitions
│   │   ├── VehicleState.msg
│   │   ├── DetectedTarget.msg
│   │   ├── DetectedTargetArray.msg
│   │   ├── TrackedTarget.msg
│   │   ├── SafetyStatus.msg
│   │   └── MissionStatus.msg
│   └── action/               # 2 action definitions
│       ├── Takeoff.action
│       └── Land.action       # Note: HoldPosition.action does NOT exist
│
└── uav_control/              # ✅ EXISTS - Partially Complete
    ├── uav_control/
    │   ├── vehicle_fsm.py           # ✅ Complete, tested
    │   ├── vehicle_state_node.py    # ✅ Complete, needs tests
    │   └── vehicle_controller.py    # 🟡 Partial (Takeoff/Land work, no movement)
    └── test/
        ├── test_vehicle_fsm.py      # ✅ 8 tests, all pass
        ├── test_vehicle_controller.py # ✅ 5 tests
        └── test_vehicle_state_node.py # ❓ Needs verification
```

### 1.2 What Actually Works (Verified in Code)

| Component | Status | Evidence |
|-----------|--------|----------|
| Docker environment | ✅ Works | Makefile, compose files exist |
| SITL + Gazebo | ✅ Works | Documented in learning logs with verification |
| MAVROS integration | ✅ Works | Service clients in vehicle_controller.py |
| Vehicle FSM | ✅ Works | 7 states, 9 transitions, 8 passing tests |
| VehicleStateNode | ✅ Works | Publishes /vehicle/state at 10Hz |
| Takeoff action | ✅ Works | Uses NAV_TAKEOFF via MAVROS |
| Land action | ✅ Works | Uses NAV_LAND via MAVROS |
| 20Hz setpoint streaming | ❌ COMMENTED OUT | Lines 105-118 in vehicle_controller.py |
| Position control | ❌ NOT IMPLEMENTED | No FlyToPosition action |
| HoldPosition action | ❌ INTENTIONALLY REMOVED | ArduPilot holds automatically |
| FSM integration with controller | ❌ NOT DONE | _is_takeoff_allowed() returns True always |

### 1.3 Critical Architecture Discovery

The learning log from 2025-12-25 contains a **verified and crucial** discovery about ArduPilot:

```
ArduPilot Two-Layer Control Model
┌─────────────────────────────────────────────┐
│   FLIGHT PHASE CONTROL (Native Commands)    │
│   - NAV_TAKEOFF required to lift off        │
│   - NAV_LAND for controlled descent         │
│   - After takeoff: GUIDED Loiter (auto-hold)│
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   POSITION CONTROL (Setpoint Streaming)     │
│   - ONLY for active movement while airborne │
│   - NOT required to maintain hover          │
│   - ArduPilot holds autonomously in GUIDED  │
└─────────────────────────────────────────────┘
```

**Implications verified in code:**
- ✅ Takeoff uses `/mavros/cmd/takeoff` service (not position setpoints)
- ✅ Land uses `/mavros/cmd/land` service
- ✅ HoldPosition action was correctly removed (not needed)
- ❌ Setpoint streaming for movement is commented out

---

## Part 2: Documentation vs Reality Gaps

### 2.1 Claims That Don't Match Code

| Documentation Claim | Reality |
|---------------------|---------|
| "80%+ coverage with unit, integration, and SITL tests" | ~20 tests total, no integration tests, no SITL tests |
| "HoldPosition action" in roadmap | Intentionally not implemented (correct decision) |
| "Phase 1 Complete" | Setpoint streaming disabled, no position control |
| "Test-Driven Development" | Some tests written after implementation |
| "Behavior tree framework" | Not started |

### 2.2 Learning Log Accuracy Assessment

| Log | Accuracy | Notes |
|-----|----------|-------|
| 2025-11-28 Docker setup | ✅ High | Verified working |
| 2025-12-01 Week1 validation | ✅ High | Commands work |
| 2025-12-02 Package architecture | ✅ High | Good learning, applied |
| 2025-12-04 uav_msgs package | ✅ High | Package exists, builds |
| 2025-12-08 Vehicle FSM | ✅ High | FSM implemented correctly |
| 2025-12-10 Actions | 🟡 Medium | HoldPosition defined but later removed |
| 2025-12-12 Takeoff action server | 🟡 Medium | Callback issue mentioned, appears resolved |
| 2025-12-25 ArduPilot fix | ✅ High | Critical discovery, correctly applied |

---

## Part 3: Architectural Quality Assessment

### 3.1 What's Done Well

1. **Proper Layered Architecture**
   - Clear separation: msgs → control → (future: perception, mission)
   - Dependency direction correct (lower layers don't depend on upper)

2. **Lifecycle Node Pattern**
   - Both VehicleStateNode and VehicleController use lifecycle
   - Enables deterministic startup/shutdown

3. **FSM Design**
   - Clean state machine with proper transitions
   - Emergency paths implemented
   - Unit tests verify behavior

4. **ArduPilot Understanding**
   - Two-layer control model understood
   - Correct use of NAV commands vs setpoints

### 3.2 Architectural Gaps

1. **FSM Not Enforced**
   - VehicleController has `_is_takeoff_allowed()` returning True always
   - FSM exists but doesn't gate operations
   - Risk: Can command takeoff from any state

2. **No Node Coordination**
   - VehicleStateNode and VehicleController are independent
   - No shared state or synchronization
   - FSM state doesn't reflect actual flight phase

3. **Missing Safety Monitor**
   - SafetyStatus message defined but no SafetyMonitor node
   - No geofence, battery monitoring, or failsafe logic

4. **Incomplete Control Layer**
   - Can takeoff and land
   - Cannot move to a position (setpoint streaming disabled)
   - No yaw control for search behavior

---

## Part 4: Refreshed Implementation Plan

### Phase 1B: Foundation Completion (Priority: HIGH)

**Goal:** Complete control layer before moving to perception.

#### Task 1.1: Enable Position Control (Est: 2-3 hours)
```python
# Currently in vehicle_controller.py (lines 105-107):
# self.setpoint_timer = self.create_timer(0.05, self._publish_setpoint)

# Action: Uncomment and add control mode flag
self.control_mode = 'IDLE'  # IDLE, POSITION
```

**Deliverables:**
- [ ] Uncomment setpoint timer
- [ ] Add control_mode state variable
- [ ] Only publish setpoints when in POSITION mode
- [ ] Test that setpoints publish at 20Hz when active

#### Task 1.2: Implement FlyToPosition Action (Est: 3-4 hours)

**Create `src/uav_msgs/action/FlyToPosition.action`:**
```
# Goal
float32 x
float32 y
float32 z
float32 yaw_deg
float32 timeout_sec
---
# Result
bool success
string message
---
# Feedback
float32 distance_remaining_m
float32 time_elapsed_sec
```

**Deliverables:**
- [ ] Create FlyToPosition.action
- [ ] Implement action server in VehicleController
- [ ] Test position control in SITL

#### Task 1.3: Implement Yaw Control (Est: 2 hours)

Required for search behavior (rotate to find target).

**Create `src/uav_msgs/action/YawTo.action`:**
```
# Goal
float32 target_yaw_deg
float32 yaw_rate_deg_s
float32 timeout_sec
---
# Result
bool success
float32 final_yaw_deg
---
# Feedback
float32 current_yaw_deg
float32 yaw_error_deg
```

#### Task 1.4: Integrate FSM with Controller (Est: 2-3 hours)

**Current problem:**
```python
def _is_takeoff_allowed(self) -> bool:
    return True  # Always allows takeoff!
```

**Solution:**
- Subscribe to /vehicle/state from VehicleStateNode
- Gate operations based on FSM state

**Deliverables:**
- [ ] VehicleController subscribes to /vehicle/state
- [ ] _is_takeoff_allowed() checks FSM state
- [ ] Add is_land_allowed(), is_move_allowed()
- [ ] Add unit tests for state gating

---

### Phase 2: Perception Pipeline (Est: 15-20 hours)

**Dependencies:** Phase 1B complete, Gazebo camera working

#### Task 2.1: Gazebo Camera Setup (Est: 3-4 hours)

**Deliverables:**
- [ ] Camera model attached to drone in Gazebo
- [ ] Verify /camera/image_raw and /camera/camera_info topics
- [ ] Correct TF: base_link → camera_link → camera_optical_frame
- [ ] Test image visible in rqt_image_view

#### Task 2.2: ArUco Marker in Simulation (Est: 2 hours)

**Deliverables:**
- [ ] Create ArUco marker model (ID: 42, size: 0.15m)
- [ ] Add to Gazebo world at known position
- [ ] Verify visible in camera when drone hovers

#### Task 2.3: ArUco Detector Node (Est: 4-5 hours)

**Create `src/uav_perception/` package:**

```python
class ArucoDetector(Node):
    def __init__(self):
        # Subscribe: /camera/image_raw, /camera/camera_info
        # Publish: /detection/targets (DetectedTargetArray)
        # Publish: /detection/debug_image (optional)
```

**Deliverables:**
- [ ] Create uav_perception package
- [ ] Implement ArucoDetector node
- [ ] Pose estimation using cv2.aruco.estimatePoseSingleMarkers
- [ ] Unit tests with known test images
- [ ] Integration test in SITL

#### Task 2.4: Target Tracker Node (Est: 3-4 hours)

**Deliverables:**
- [ ] Implement simple low-pass filter for pose smoothing
- [ ] Track persistence (1s timeout on detection loss)
- [ ] Publish /tracking/targets (TrackedTarget)

---

### Phase 3: Simple Mission (Est: 12-15 hours)

**Dependencies:** Phase 2 complete

#### Task 3.1: py_trees Integration (Est: 4-5 hours)

**Create `src/uav_mission/` package:**

**Deliverables:**
- [ ] Install py_trees, py_trees_ros
- [ ] Create base classes: RosActionBehavior, RosCondition
- [ ] Wrap existing actions: TakeoffBehavior, LandBehavior

#### Task 3.2: Search Behavior (Est: 4-5 hours)

```python
class RotateSearchBehavior(py_trees.behaviour.Behaviour):
    """Rotate 360° in steps until target detected."""
    # Uses YawTo action
    # Checks /tracking/targets for detection
```

**Deliverables:**
- [ ] Implement RotateSearchBehavior
- [ ] Test in SITL with marker at various angles

#### Task 3.3: Complete Search Mission (Est: 3-4 hours)

```
Mission Tree:
Sequence("search_mission")
├── TakeoffBehavior(altitude=3.0)
├── Fallback("search")
│   ├── TargetDetected()
│   └── RotateSearchBehavior()
├── WaitBehavior(duration=5.0)  # ArduPilot holds automatically
└── LandBehavior()
```

**Deliverables:**
- [ ] Assemble mission tree
- [ ] Mission executor node
- [ ] Test complete mission in SITL

---

### Phase 4: Visual Servoing & Full Mission

**Defer until Phase 3 validated.**

---

## Part 5: Prioritized Action Items

### Immediate (This Week)

1. **Fix setpoint streaming** - Uncomment timer, add control mode
2. **Implement FlyToPosition action** - Required for any movement
3. **Integrate FSM with controller** - Safety-critical

### Short-term (Next 2 Weeks)

4. **Camera pipeline in Gazebo** - Blocks perception
5. **ArUco detector** - Core perception capability
6. **Basic target tracking** - Smooth detections

### Medium-term (Weeks 3-4)

7. **py_trees integration** - Mission framework
8. **Search behavior** - First mission component
9. **Complete search mission** - End-to-end validation

---

## Part 6: Quality Standards Going Forward

### Testing Requirements

1. **Unit Tests (Required for merge)**
   - All new code must have tests
   - Test both valid and invalid inputs
   - FSM transitions must be tested

2. **Integration Tests (Required for phase completion)**
   - Multi-node tests using launch_testing
   - Verify inter-node communication

3. **SITL Tests (Required for each action)**
   - Automated flight tests
   - Record rosbags for debugging

### Code Review Checklist

- [ ] FSM state checked before operations
- [ ] Error handling for service call failures
- [ ] Timeout handling for long operations
- [ ] Logger messages for debugging
- [ ] Type hints on public methods
- [ ] Docstrings on classes and complex methods

### Documentation Standards

- [ ] Update README when features complete
- [ ] Learning logs for non-trivial sessions
- [ ] Comments only where code isn't self-evident

---

## Part 7: Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gazebo camera setup issues | Medium | High | Budget extra time, have fallback (image from file) |
| py_trees complexity | Medium | Medium | Start with simple behaviors, add complexity incrementally |
| SITL timing issues | High | Medium | Use longer timeouts, add retries |
| Integration bugs | High | Medium | Test nodes individually first |

---

## Conclusion

The project has a solid foundation with key insights about ArduPilot behavior correctly applied. The main gaps are:

1. **Position control disabled** - Quick fix needed
2. **FSM not enforced** - Safety gap
3. **No perception pipeline** - Phase 2 not started

The refreshed plan focuses on completing Phase 1B before moving to perception, ensuring the control layer is fully functional before adding complexity.

**Recommended next action:** Enable setpoint streaming and implement FlyToPosition action, as these unblock all subsequent phases.

---

*Document Version: 1.0*
*Generated: 2025-12-29*
