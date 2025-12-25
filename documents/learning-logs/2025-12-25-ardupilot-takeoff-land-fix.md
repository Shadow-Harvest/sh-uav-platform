# Learning Log: ArduPilot Takeoff/Land Fix & TDD

**Date:** 2025-12-25

**Session:** Week 3 - Fixing Drone Disarm Bug & Implementing Land Action

**Duration:** ~2 hours

**Status:** ✅ Complete - Takeoff and Land actions working correctly

---

## 🎯 Session Objectives

1. ✅ Diagnosed silent disarm bug after arming
2. ✅ Understood ArduPilot vs PX4 takeoff differences
3. ✅ Implemented proper NAV_TAKEOFF command
4. ✅ Implemented Land action using TDD
5. ✅ Merged to develop branch

---

## 🐛 The Bug

**Symptom:** Drone silently disarmed immediately after arming during takeoff.

**Root Cause:** Trying to takeoff using position setpoints alone. ArduPilot requires explicit `NAV_TAKEOFF` command - position setpoints only work for control once already airborne.

**Key Finding from ArduPilot/MAVROS Documentation:**
> "It is required to call the takeoff service BEFORE sending position setpoints to setpoint_position/local."

---

## 📚 Key Concepts Learned

### 1. ArduPilot Two-Layer Control Model

ArduPilot separates control into two distinct layers:

```
┌─────────────────────────────────────────────┐
│   POSITION CONTROL (setpoint streaming)     │
│   - Fly to waypoint                         │
│   - Hold position                           │
│   - ONLY works when AIRBORNE                │
└─────────────────────────────────────────────┘
                    ↑
          (enabled after takeoff)
                    ↑
┌─────────────────────────────────────────────┐
│   FLIGHT PHASE CONTROL (native commands)    │
│   - /mavros/cmd/takeoff (NAV_TAKEOFF)       │
│   - /mavros/cmd/land (NAV_LAND)             │
│   - ArduPilot handles these INTERNALLY      │
└─────────────────────────────────────────────┘
```

| Layer | Responsibility | MAVROS Interface |
|-------|---------------|------------------|
| **Flight Phase Control** | Ground↔Air transitions | Services: `/mavros/cmd/takeoff`, `/mavros/cmd/land` |
| **Position Control** | Movement while airborne | Topic: `/mavros/setpoint_position/local` @ 20Hz |

### 2. Correct ArduPilot Takeoff Sequence

```
1. Set GUIDED mode      → /mavros/set_mode
2. Arm                  → /mavros/cmd/arming
3. Takeoff command      → /mavros/cmd/takeoff  ← This actually lifts the drone!
4. Monitor altitude     → Wait until target reached
5. Position control     → Setpoints take over for movement
```

**Critical insight:** Position setpoints cannot make ArduPilot take off from ground. They only work for position control once already airborne.

### 3. ArduPilot GUIDED Loiter Behavior

After `NAV_TAKEOFF` completes, ArduPilot enters **GUIDED Loiter** mode:
- Holds position autonomously
- Does NOT require continuous setpoints to stay airborne
- Only triggers failsafe on GCS heartbeat loss (not setpoint loss)

This is a safety feature - the drone won't fall out of the sky if you stop sending commands.

### 4. Test-Driven Development (TDD) Cycle

```
RED → GREEN → REFACTOR
 │       │        │
 │       │        └─ Clean up if needed
 │       └─ Write minimal code to pass
 └─ Write failing test first
```

**Example test written first (RED):**
```python
def test_takeoff_calls_mavros_takeoff_service_after_arming(self, node):
    """Takeoff must call MAVROS takeoff command after arming."""
    node._mavros_takeoff = MagicMock(return_value=True)
    # ... setup ...
    node._execute_takeoff(goal_handle)

    assert node._mavros_takeoff.called, (
        "Takeoff must call _mavros_takeoff() to send NAV_TAKEOFF command"
    )
```

### 5. CommandTOL Service Interface

Both takeoff and land use `mavros_msgs/srv/CommandTOL`:

```python
request = CommandTOL.Request()
request.altitude = altitude  # Target altitude (0 for land)
request.latitude = 0.0       # 0 = use current location
request.longitude = 0.0      # 0 = use current location
request.min_pitch = 0.0
request.yaw = 0.0
```

### 6. Landing Logic Gotchas

Common bugs when implementing land:

| Bug | Wrong | Correct |
|-----|-------|---------|
| Altitude check | `current_alt >= target - 0.2` | `current_alt <= 0.3` |
| Progress calc | `current / target` (div by 0!) | `current / starting_altitude` or omit |
| Result fields | Including non-existent fields | Check action definition first |

---

## 🏗️ What Was Built

### Updated Takeoff Sequence

```python
def _execute_takeoff(self, goal_handle):
    # Step 1: Set GUIDED mode
    if not self._set_mode('GUIDED'):
        return abort("Failed to set GUIDED mode")

    # Step 2: Arm the vehicle
    if not self._arm_vehicle(True):
        return abort("Failed to arm vehicle")

    # Step 3: Command takeoff via MAVROS  ← NEW!
    if not self._mavros_takeoff(target_altitude):
        return abort("MAVROS takeoff command failed")

    # Step 4: Monitor altitude until reached
    while not at_altitude:
        publish_feedback()
        spin_once()
```

### New Land Action

```python
def _execute_land(self, goal_handle):
    # Command land via MAVROS
    if not self._mavros_land():
        return abort("MAVROS land command failed")

    # Monitor altitude until near ground
    while current_alt > 0.3:
        publish_feedback()
        spin_once()

    return success()
```

### New Service Clients

```python
self.takeoff_client = self.create_client(CommandTOL, '/mavros/cmd/takeoff')
self.land_client = self.create_client(CommandTOL, '/mavros/cmd/land')
```

---

## 🔧 Commands Reference

```bash
# Test takeoff
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 5.0, timeout_sec: 30.0}"

# Test land
ros2 action send_goal /vehicle/land uav_msgs/action/Land \
  "{timeout_sec: 30.0}"

# Monitor altitude
ros2 topic echo /mavros/local_position/pose --field pose.position.z
```

---

## 📊 Session Stats

- Files modified: 2 (`vehicle_controller.py`, `test_vehicle_controller.py`)
- Tests added: 2 (takeoff service call, land service call)
- Bugs fixed: 1 major (silent disarm on takeoff)
- Features added: 1 (Land action)
- Commits: 2 (`Transition to MAVROS takeoff command`, `Implement Land action`)

---

## 💡 Key Insights

1. **ArduPilot ≠ PX4** - Takeoff behavior differs significantly. Always check flight controller docs.
2. **Position setpoints are for movement, not takeoff** - NAV_TAKEOFF is required to get airborne.
3. **ArduPilot is fail-safe** - Holds position after takeoff even without setpoints.
4. **TDD catches bugs early** - Writing tests first forced thinking about edge cases (like landing altitude check).
5. **Check action definitions** - Don't assume fields exist; verify against `.action` files.

---

## ✅ Self-Assessment

Can I now:
- ✅ Explain why position setpoints don't work for ArduPilot takeoff? YES
- ✅ Implement proper takeoff using NAV_TAKEOFF? YES
- ✅ Implement land action with correct altitude monitoring? YES
- ✅ Use TDD approach (RED → GREEN → REFACTOR)? YES
- ✅ Debug ArduPilot-specific issues using documentation? YES

**Confidence level:** 9/10 - Core flight phase control understood

**Achievement unlocked:** 🛬 First Autonomous Landing

**Session vibe:** "The bug that taught me ArduPilot internals"

---

## 🚀 What's Next

1. Re-enable 20Hz setpoint streaming for position control
2. Implement HoldPosition action
3. Implement FlyToPosition action (uses setpoint streaming)
4. Integration test: Takeoff → Fly to waypoint → Return → Land
