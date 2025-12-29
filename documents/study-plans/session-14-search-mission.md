# Session 14: Complete Search Mission

**Phase:** 3 - Mission Framework
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium
**PHASE GATE:** This session completes Phase 3

---

## Prerequisites

- [ ] Sessions 10-13 complete
- [ ] All behaviors and executor working
- [ ] SITL with perception pipeline running

---

## Learning Objectives

By the end of this session, you will understand:

1. **Mission composition** - assembling behaviors into complete missions
2. **End-to-end testing** - validating autonomous operation
3. **Debugging behavior trees** - finding and fixing issues
4. **Mission parameterization** - configurable missions

---

## Practical Objectives

### Primary Goal
Assemble and validate complete search mission: Takeoff → Search → Wait → Land

### Deliverables

1. **Create search mission tree:**
   ```
   Sequence("search_mission")
   ├── TakeoffBehavior(altitude=3.0)
   ├── Selector("find_target")
   │   ├── IsTargetVisible()          # Already visible?
   │   └── RotateSearchBehavior()     # Search for it
   ├── SuccessToRunning(Wait(5.0))    # Hold position
   └── LandBehavior()
   ```

2. **Create mission factory:**
   - `create_search_mission(altitude, search_params)` function
   - Returns configured tree
   - Parameterizable

3. **End-to-end SITL test:**
   - Marker placed behind drone at start
   - Mission runs autonomously
   - Drone finds marker, waits, lands

4. **Add mission launch file:**
   - Starts all required nodes
   - Configures mission parameters

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Design mission tree, review all behaviors |
| 0:30-1:15 | Implement mission factory |
| 1:15-1:45 | Create launch file for full stack |
| 1:45-2:30 | SITL testing - debug issues |
| 2:30-3:15 | Iterate on problems found |
| 3:15-3:45 | Record successful run |
| 3:45-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Full stack launch
ros2 launch uav_mission search_mission.launch.py

# 2. Mission runs autonomously
# - Drone takes off to 3m
# - Rotates searching for marker
# - Finds marker (stops rotating)
# - Waits 5 seconds
# - Lands safely

# 3. Mission completes with SUCCESS
ros2 topic echo /mission/status
# Should show SUCCESS at end

# 4. Test failure case
# Remove marker from world
# Mission should FAIL after full rotation

# 5. Record rosbag for documentation
ros2 bag record -a -o search_mission_demo
```

---

## Key Questions to Answer During Session

1. What if takeoff fails? How does tree handle it?
2. What if detection is lost during wait? (Continue waiting)
3. How to abort mission mid-flight? (Manual control takeover)
4. What state is drone in after mission failure?

---

## Mission Tree Implementation

```python
def create_search_mission(
    node,
    takeoff_altitude=3.0,
    search_step_deg=30.0,
    search_pause_sec=2.0,
    hold_duration_sec=5.0
):
    """Create a search mission behavior tree."""

    root = py_trees.composites.Sequence("search_mission", memory=True)

    # Phase 1: Takeoff
    takeoff = TakeoffBehavior(
        "takeoff",
        node,
        altitude=takeoff_altitude,
        timeout=30.0
    )

    # Phase 2: Search for target
    search_selector = py_trees.composites.Selector("find_target", memory=False)
    already_visible = IsTargetVisible("already_visible", node)
    rotate_search = RotateSearchBehavior(
        "rotate_search",
        node,
        step_deg=search_step_deg,
        pause_sec=search_pause_sec
    )
    search_selector.add_children([already_visible, rotate_search])

    # Phase 3: Hold position (ArduPilot holds automatically)
    # SuccessToRunning converts immediate SUCCESS to RUNNING for duration
    hold = py_trees.decorators.Timeout(
        "hold",
        child=py_trees.behaviours.Running("holding"),
        duration=hold_duration_sec
    )

    # Phase 4: Land
    land = LandBehavior("land", node, timeout=30.0)

    # Assemble
    root.add_children([takeoff, search_selector, hold, land])

    return root
```

---

## Launch File

```python
# src/uav_mission/launch/search_mission.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    return LaunchDescription([
        # Include perception
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                'install/uav_perception/share/uav_perception/launch/perception.launch.py'
            ])
        ),

        # Mission executor with search mission
        Node(
            package='uav_mission',
            executable='mission_executor',
            name='mission_executor',
            parameters=[{
                'mission_type': 'search',
                'takeoff_altitude': 3.0,
                'search_step_deg': 30.0,
                'hold_duration': 5.0
            }]
        ),
    ])
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Detection flaky | Search doesn't stop | Lower threshold, increase pause |
| Takeoff fails | Mission aborts early | Check FSM state, MAVROS |
| Tree structure wrong | Unexpected behavior | Visualize with py_trees |
| Timing issues | Behaviors race | Add delays, check ordering |
| Land rejected | Stuck after search | Verify FSM allows land |

---

## Code Locations

- Mission factory: `src/uav_mission/uav_mission/missions/search.py`
- Launch file: `src/uav_mission/launch/search_mission.launch.py`
- Tests: `src/uav_mission/test/test_search_mission.py`

---

## Definition of Done

- [ ] Search mission tree assembled
- [ ] Mission factory function created
- [ ] Launch file starts full stack
- [ ] SITL: Takeoff succeeds
- [ ] SITL: Search finds marker
- [ ] SITL: Hold maintains position
- [ ] SITL: Land completes
- [ ] Mission status shows SUCCESS
- [ ] Failure case tested (no marker)
- [ ] Rosbag recorded for documentation
- [ ] Committed with descriptive message

---

## Phase 3 Gate Criteria

Before proceeding to Phase 4, verify:

- [ ] All behaviors work individually
- [ ] Mission executor ticks tree properly
- [ ] Search mission runs end-to-end
- [ ] Success case: drone finds marker, waits, lands
- [ ] Failure case: drone completes search, fails, lands (or holds)
- [ ] All unit tests pass
- [ ] Document lessons learned

**Congratulations!** Phase 3 complete. You have a working autonomous search mission.

---

## Notes for Next Session

Phase 4 begins with Session 15: Approach Controller Theory. You'll learn visual servoing concepts before implementing target approach.
