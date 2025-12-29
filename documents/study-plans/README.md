# Study Session Plans

> Master index for all study sessions to complete the SH-UAV-Platform project.

**Total Estimated Sessions:** 18-22 sessions
**Average Session Length:** 2-4 hours
**Total Project Hours:** ~60-80 hours remaining

---

## How to Use These Plans

Each session plan contains:
1. **Prerequisites** - What must be done before starting
2. **Learning Objectives** - What you'll understand after
3. **Practical Objectives** - What you'll build/implement
4. **Verification Checklist** - How to confirm success
5. **Session Structure** - Suggested time breakdown
6. **Potential Blockers** - What might go wrong and how to handle it

---

## Phase Overview

| Phase | Sessions | Focus | Gate Criteria |
|-------|----------|-------|---------------|
| **1B** | 1-4 | Control Layer Completion | FlyToPosition works in SITL |
| **2** | 5-9 | Perception Pipeline | ArUco detected and tracked in SITL |
| **3** | 10-14 | Mission Framework | Search mission completes autonomously |
| **4** | 15-17 | Visual Servoing | Full approach mission works |
| **5** | 18-20 | Integration & Polish | CI green, documentation complete |

---

## Session Index

### Phase 1B: Control Layer Completion
- [Session 01: Position Control Activation](./session-01-position-control.md)
- [Session 02: FlyToPosition Action](./session-02-fly-to-position.md)
- [Session 03: Yaw Control](./session-03-yaw-control.md)
- [Session 04: FSM Integration & Safety](./session-04-fsm-integration.md)

### Phase 2: Perception Pipeline
- [Session 05: Gazebo Camera Setup](./session-05-gazebo-camera.md)
- [Session 06: ArUco Marker World](./session-06-aruco-world.md)
- [Session 07: ArUco Detector Node](./session-07-aruco-detector.md)
- [Session 08: Target Tracker](./session-08-target-tracker.md)
- [Session 09: Perception Integration](./session-09-perception-integration.md)

### Phase 3: Mission Framework
- [Session 10: py_trees Fundamentals](./session-10-pytrees-basics.md)
- [Session 11: ROS2 Behavior Wrappers](./session-11-ros2-behaviors.md)
- [Session 12: Search Behavior](./session-12-search-behavior.md)
- [Session 13: Mission Executor](./session-13-mission-executor.md)
- [Session 14: Complete Search Mission](./session-14-search-mission.md)

### Phase 4: Visual Servoing
- [Session 15: Approach Controller Theory](./session-15-approach-theory.md)
- [Session 16: Approach Implementation](./session-16-approach-implementation.md)
- [Session 17: Full Mission Integration](./session-17-full-mission.md)

### Phase 5: Integration & Polish
- [Session 18: Testing Infrastructure](./session-18-testing.md)
- [Session 19: CI/CD Pipeline](./session-19-cicd.md)
- [Session 20: Documentation & Portfolio](./session-20-documentation.md)

---

## Quick Start

**Before your first session:**
1. Ensure SITL environment works: `make gazebo`, `make sitl`, `make mavros`
2. Verify current code builds: `make build`
3. Run existing tests: `make test`

**Start with:** [Session 01: Position Control Activation](./session-01-position-control.md)
