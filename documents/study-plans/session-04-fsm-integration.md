# Session 04: FSM Integration & Safety

**Phase:** 1B - Control Layer Completion
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium
**PHASE GATE:** This session completes Phase 1B

---

## Prerequisites

- [ ] Sessions 01-03 complete
- [ ] All actions work in SITL (Takeoff, Land, FlyToPosition, YawTo)
- [ ] Review `vehicle_fsm.py` and `vehicle_state_node.py`

---

## Learning Objectives

By the end of this session, you will understand:

1. **State-based safety gating** - why operations must check state
2. **Inter-node communication** - subscribing to state from another node
3. **FSM transition triggers** - when to advance the state machine
4. **Defense in depth** - multiple layers of safety checks

---

## Practical Objectives

### Primary Goal
Make VehicleController respect FSM state - operations only allowed in valid states.

### Deliverables

1. **VehicleController subscribes to /vehicle/state:**
   - Add subscriber for VehicleState message
   - Store current FSM state
   - Implement state checking methods

2. **Implement state guards:**
   ```python
   def _is_takeoff_allowed(self) -> bool:
       # Only from ARMED state
       return self.current_fsm_state == VehicleState.STATE_ARMED

   def _is_land_allowed(self) -> bool:
       # Only from FLYING or HOVERING (mapped to STATE_FLYING)
       return self.current_fsm_state == VehicleState.STATE_FLYING

   def _is_move_allowed(self) -> bool:
       # Only when airborne
       return self.current_fsm_state == VehicleState.STATE_FLYING
   ```

3. **FSM state updates from controller:**
   - After successful takeoff: trigger `takeoff_complete`
   - After successful land: trigger `touchdown`
   - During movement: consider `navigate` / `target_reached`

4. **Service for FSM transitions:**
   - Create service in VehicleStateNode for external transition triggers
   - VehicleController calls service after action completion

5. **Unit tests:**
   - Test takeoff rejected when not ARMED
   - Test land rejected when not flying
   - Test FlyToPosition rejected when grounded

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:20 | Review FSM states, plan integration approach |
| 0:20-0:40 | Add VehicleState subscription to controller |
| 0:40-1:10 | Implement state guard methods |
| 1:10-1:40 | Create FSM transition service |
| 1:40-2:10 | Integrate actions with FSM transitions |
| 2:10-2:40 | Write unit tests |
| 2:40-3:00 | SITL verification, commit |

---

## Verification Checklist

```bash
# 1. Build succeeds
make build

# 2. Unit tests for state guards pass
pytest src/uav_control/test/ -v -k "allowed"

# 3. SITL: Verify takeoff rejected when disarmed
# (Don't arm first, try takeoff - should fail)
ros2 action send_goal /vehicle/takeoff uav_msgs/action/Takeoff \
  "{target_altitude_m: 3.0, timeout_sec: 30.0}"
# Expected: Goal rejected or aborted with message about state

# 4. SITL: Full sequence with FSM transitions
# Should see /vehicle/state topic showing state changes
ros2 topic echo /vehicle/state &
# Takeoff (should transition ARMED → TAKING_OFF → FLYING)
# Land (should transition FLYING → LANDING → DISARMED)
```

---

## Key Questions to Answer During Session

1. How should VehicleController and VehicleStateNode coordinate?
2. Who is responsible for triggering FSM transitions?
3. What if state update is delayed - how to handle race conditions?
4. Should emergency trigger be in controller or state node?

---

## Design Decision: Coordination Pattern

**Option A: Controller triggers FSM directly (tight coupling)**
```
VehicleController → calls FSM methods on VehicleStateNode
```
Pros: Simple, synchronous
Cons: Tight coupling, harder to test

**Option B: Service-based transition (loose coupling)**
```
VehicleController → calls /vehicle/fsm_transition service → VehicleStateNode
```
Pros: Decoupled, testable, can add validation
Cons: Async complexity

**Option C: Event-based (publish/subscribe)**
```
VehicleController → publishes /vehicle/events → VehicleStateNode
```
Pros: Very decoupled
Cons: Fire-and-forget, no confirmation

**Recommended:** Option B - Service-based with confirmation

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| State updates delayed | Guard passes but shouldn't | Add timeout, retry logic |
| Service call fails | Transition not recorded | Log error, consider retry |
| Node startup order | Subscriber gets no messages | Wait for first message |
| State mismatch | Controller thinks ARMED, node thinks DISARMED | Debug with topic echo |

---

## Code Locations

- Controller: `src/uav_control/uav_control/vehicle_controller.py`
- State node: `src/uav_control/uav_control/vehicle_state_node.py`
- FSM: `src/uav_control/uav_control/vehicle_fsm.py`
- New service: Consider `src/uav_msgs/srv/TriggerTransition.srv`

---

## State Mapping Reference

| FSM State | VehicleState.msg Constant |
|-----------|---------------------------|
| disarmed | STATE_DISARMED (1) |
| armed | STATE_ARMED (2) |
| taking_off | STATE_TAKING_OFF (3) |
| hovering | STATE_FLYING (4) |
| flying | STATE_FLYING (4) |
| landing | STATE_LANDING (5) |
| emergency | STATE_EMERGENCY (7) |

Note: `hovering` and `flying` both map to STATE_FLYING in the message.

---

## Definition of Done

- [ ] VehicleController subscribes to /vehicle/state
- [ ] State guard methods implemented for all actions
- [ ] Takeoff rejected when not ARMED
- [ ] Land rejected when not FLYING
- [ ] FlyToPosition rejected when not FLYING
- [ ] FSM transitions triggered after action completion
- [ ] At least 4 new unit tests
- [ ] SITL: Full takeoff→fly→land sequence with correct state transitions
- [ ] Committed with descriptive message

---

## Phase 1B Gate Criteria

Before proceeding to Phase 2, verify:

- [ ] All control actions work: Takeoff, Land, FlyToPosition, YawTo
- [ ] 20Hz setpoint streaming active during movement
- [ ] FSM guards prevent invalid operations
- [ ] State transitions tracked correctly
- [ ] All unit tests pass: `make test`
- [ ] Document lessons learned

**Congratulations!** Phase 1B complete. You now have a fully functional control layer.

---

## Notes for Next Session

Phase 2 begins with Session 05: Gazebo Camera Setup. You'll add a camera to the drone and verify image streaming before implementing perception.
