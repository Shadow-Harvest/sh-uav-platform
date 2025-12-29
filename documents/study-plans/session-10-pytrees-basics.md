# Session 10: py_trees Fundamentals

**Phase:** 3 - Mission Framework
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium (conceptual learning)

---

## Prerequisites

- [ ] Phase 2 complete (perception pipeline works)
- [ ] Python comfortable
- [ ] No prior behavior tree knowledge required

---

## Learning Objectives

By the end of this session, you will understand:

1. **Behavior tree structure** - nodes, composites, decorators
2. **Execution model** - tick, status, blackboard
3. **Composite types** - Sequence, Selector (Fallback), Parallel
4. **py_trees API** - creating trees programmatically

---

## Practical Objectives

### Primary Goal
Understand behavior trees deeply, build simple examples, prepare for ROS2 integration.

### Deliverables

1. **Install and explore py_trees:**
   ```bash
   pip install py_trees py_trees_ros
   ```

2. **Build example trees (in Python REPL or scripts):**
   - Simple sequence: Action1 → Action2 → Action3
   - Fallback: TryA | TryB | TryC (first success wins)
   - Condition checking: IsConditionMet → DoAction

3. **Understand blackboard:**
   - Shared data storage
   - Read/write from behaviors
   - Scope and namespacing

4. **Document key concepts** in learning log

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:45 | Read py_trees documentation, understand concepts |
| 0:45-1:15 | Build and run simple Sequence example |
| 1:15-1:45 | Build and run Fallback (Selector) example |
| 1:45-2:15 | Explore Blackboard usage |
| 2:15-2:45 | Study py_trees_ros examples |
| 2:45-3:30 | Design mission tree on paper |
| 3:30-4:00 | Document learnings |

---

## Key Concepts

### Behavior Node Status

```
SUCCESS  - Task completed successfully
FAILURE  - Task failed (not an error, just didn't succeed)
RUNNING  - Task still in progress
```

### Composite Types

```
SEQUENCE (→)
├── Child1  ✓ (must succeed to continue)
├── Child2  ✓ (must succeed to continue)
└── Child3  ✓ → SUCCESS (all succeeded)

SELECTOR / FALLBACK (?)
├── Child1  ✗ (failed, try next)
├── Child2  ✓ → SUCCESS (first success wins)
└── Child3     (never executed)

PARALLEL (⇒)
├── Child1  RUNNING
├── Child2  SUCCESS
└── Child3  RUNNING  → depends on policy
```

### Blackboard Pattern

```python
import py_trees

# Write
blackboard = py_trees.blackboard.Client(name="Writer")
blackboard.register_key(key="target_position", access=py_trees.common.Access.WRITE)
blackboard.target_position = (3.0, 3.0, 3.0)

# Read
reader = py_trees.blackboard.Client(name="Reader")
reader.register_key(key="target_position", access=py_trees.common.Access.READ)
position = reader.target_position
```

---

## Verification Checklist

```python
# 1. py_trees installed
import py_trees
print(py_trees.__version__)

# 2. Simple sequence runs
root = py_trees.composites.Sequence("test", memory=True)
root.add_children([
    py_trees.behaviours.Success(name="Step1"),
    py_trees.behaviours.Success(name="Step2"),
])
root.setup_with_descendants()
for _ in range(3):
    root.tick_once()
print(root.status)  # Should be SUCCESS

# 3. Blackboard works
blackboard = py_trees.blackboard.Client(name="test")
blackboard.register_key(key="foo", access=py_trees.common.Access.WRITE)
blackboard.foo = "bar"
print(blackboard.foo)  # Should print "bar"
```

---

## Key Questions to Answer During Session

1. What's the difference between Sequence and Selector?
2. When does a RUNNING status propagate up?
3. What's the purpose of `memory` in composites?
4. How do decorators modify behavior (Inverter, Retry, Timeout)?
5. Why use Blackboard instead of passing data directly?

---

## Example: Search Mission Conceptual Tree

```
Sequence("search_mission")
├── TakeoffAction(altitude=3.0)
├── Selector("find_target")
│   ├── TargetInView()           # Condition: already see target
│   └── RotateSearch(step=30°)   # Action: rotate until found
├── Wait(5.0)                    # Let ArduPilot hold position
└── LandAction()
```

**Sketch this tree on paper** during the session!

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Import error | py_trees not found | pip install in correct environment |
| Tree doesn't tick | No status change | Call tick_once() in loop |
| Blackboard key error | Key not found | Register before access |
| Status confusion | Wrong behavior | Study SUCCESS/FAILURE/RUNNING |

---

## Code Locations

- Examples: Create in `scripts/pytrees_examples/`
- Later: `src/uav_mission/`

---

## Resources

- py_trees docs: https://py-trees.readthedocs.io/
- py_trees_ros: https://github.com/splintered-reality/py_trees_ros
- Behavior Trees in Robotics (paper): Worth reading for theory

---

## Definition of Done

- [ ] py_trees installed and importing
- [ ] Can create and tick a Sequence
- [ ] Can create and tick a Selector
- [ ] Understand Blackboard read/write
- [ ] Sketched search mission tree on paper
- [ ] Learning log updated with key concepts
- [ ] Ready to integrate with ROS2

---

## Notes for Next Session

Session 11 will create ROS2-aware behavior wrappers for your existing actions (Takeoff, Land, FlyToPosition).
