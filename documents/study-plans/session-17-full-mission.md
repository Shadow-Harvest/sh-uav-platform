# Session 17: Full Mission Integration

**Phase:** 4 - Visual Servoing
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium
**PHASE GATE:** This session completes Phase 4

---

## Prerequisites

- [ ] Sessions 15-16 complete
- [ ] Search mission working
- [ ] Approach behavior working
- [ ] Full SITL stack ready

---

## Learning Objectives

By the end of this session, you will understand:

1. **Mission composition** - combining search and approach
2. **Data flow via blackboard** - passing target between behaviors
3. **Error recovery** - handling failures mid-mission
4. **Mission variants** - parameterizable mission trees

---

## Practical Objectives

### Primary Goal
Create complete Search-and-Approach mission that runs fully autonomously.

### Deliverables

1. **Create full mission tree:**
   ```
   Sequence("search_approach_mission")
   ├── TakeoffBehavior(altitude=5.0)
   ├── Selector("find_target")
   │   ├── IsTargetVisible()
   │   └── RotateSearchBehavior()
   ├── ApproachBehavior(hover_alt=1.5)
   ├── HoverWait(duration=10.0)
   └── LandBehavior()
   ```

2. **Blackboard data flow:**
   - SearchBehavior writes target_id to blackboard
   - ApproachBehavior reads target_id from blackboard

3. **Mission variants:**
   - `search_and_approach` - full mission
   - `approach_only` - assumes target visible
   - `search_only` - no approach

4. **End-to-end SITL test:**
   - Drone starts facing away from marker
   - Searches and finds marker
   - Approaches to 1.5m hover
   - Holds for 10s
   - Lands

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Design mission tree, plan blackboard usage |
| 0:30-1:15 | Implement full mission factory |
| 1:15-1:45 | Add blackboard data passing |
| 1:45-2:30 | SITL testing - full mission |
| 2:30-3:00 | Debug and iterate |
| 3:00-3:30 | Test failure scenarios |
| 3:30-4:00 | Record demo, commit, document |

---

## Verification Checklist

```bash
# 1. Launch full mission
ros2 launch uav_mission search_approach.launch.py

# 2. Mission runs autonomously
# Watch in Gazebo:
# - Takeoff to 5m
# - Rotate searching
# - Find marker
# - Fly toward marker
# - Descend to 1.5m above
# - Hover 10s
# - Land

# 3. Check final position
ros2 topic echo /mavros/local_position/pose --once
# Should be above marker position

# 4. Record demo
ros2 bag record -a -o search_approach_demo
# Also screen record Gazebo!
```

---

## Key Questions to Answer During Session

1. How does target_id flow from search to approach?
2. What if target lost during approach? (Keep going, will re-detect)
3. Should approach use cached position or live tracking?
4. How to handle multiple markers detected?

---

## Full Mission Implementation

```python
def create_search_approach_mission(
    node,
    takeoff_altitude=5.0,
    hover_altitude=1.5,
    search_step_deg=30.0,
    search_pause_sec=2.0,
    hover_duration_sec=10.0,
    target_id=None  # None = any target
):
    """Create search-and-approach mission tree."""

    root = py_trees.composites.Sequence("search_approach_mission", memory=True)

    # Phase 1: Takeoff
    takeoff = TakeoffBehavior("takeoff", node, altitude=takeoff_altitude)

    # Phase 2: Search for target
    search = py_trees.composites.Selector("find_target", memory=False)
    already_visible = IsTargetVisible("already_visible", node, target_id)
    rotate_search = RotateSearchBehavior("search", node,
        step_deg=search_step_deg,
        pause_sec=search_pause_sec,
        target_id=target_id
    )
    search.add_children([already_visible, rotate_search])

    # Phase 3: Approach target (reads target_id from blackboard)
    approach = ApproachBehavior("approach", node,
        hover_altitude=hover_altitude,
        timeout=60.0
    )

    # Phase 4: Hover over target
    hover = py_trees.decorators.Timeout(
        "hover",
        child=py_trees.behaviours.Running("holding"),
        duration=hover_duration_sec
    )

    # Phase 5: Land
    land = LandBehavior("land", node, timeout=30.0)

    # Assemble
    root.add_children([takeoff, search, approach, hover, land])

    return root
```

---

## Blackboard Usage

```python
# In RotateSearchBehavior, on success:
def _write_target_to_blackboard(self, target):
    blackboard = py_trees.blackboard.Client(name="search")
    blackboard.register_key(key="target_id", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="target_pose", access=py_trees.common.Access.WRITE)
    blackboard.target_id = target.target_id
    blackboard.target_pose = target.pose

# In ApproachBehavior, read target:
def initialise(self):
    blackboard = py_trees.blackboard.Client(name="approach")
    blackboard.register_key(key="target_id", access=py_trees.common.Access.READ)
    self.target_id = blackboard.target_id
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Blackboard key missing | KeyError on read | Ensure search runs first |
| Target lost during approach | Approach fails | Add retry or use last known |
| Landing rejected | Stuck after hover | Check FSM state |
| Timing issues | Behaviors race | Add delays if needed |
| Gazebo slow | Mission takes forever | Reduce search pause |

---

## Code Locations

- Mission: `src/uav_mission/uav_mission/missions/search_approach.py`
- Launch: `src/uav_mission/launch/search_approach.launch.py`
- Tests: `src/uav_mission/test/test_full_mission.py`

---

## Definition of Done

- [ ] Full mission tree assembled
- [ ] Blackboard connects search to approach
- [ ] Launch file starts everything
- [ ] SITL: Takeoff works
- [ ] SITL: Search finds marker
- [ ] SITL: Approach reaches hover position
- [ ] SITL: Hover maintains position
- [ ] SITL: Land completes
- [ ] Demo recorded (rosbag + screen)
- [ ] Committed with descriptive message

---

## Phase 4 Gate Criteria

Before proceeding to Phase 5, verify:

- [ ] Approach controller works reliably
- [ ] Full mission runs end-to-end
- [ ] Failure cases handled gracefully
- [ ] Demo recorded and watchable
- [ ] All unit tests pass
- [ ] Document lessons learned

**Congratulations!** Phase 4 complete. You have a fully autonomous search-approach-land mission.

---

## Notes for Next Session

Phase 5 focuses on testing infrastructure, CI/CD, and documentation for portfolio-ready code.
