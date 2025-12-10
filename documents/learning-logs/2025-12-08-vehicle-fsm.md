# Learning Log: Vehicle Finite State Machine

 

**Date:** 2025-12-08

 

**Session:** Week 2 Day 3-4 - FSM Design & Implementation

 

**Duration:** ~3-4 hours

 

**Status:** ✅ Complete - FSM implemented and tested!

 

---

 

## 🎯 Session Objectives Achieved

 

1. ✅ Created `uav_control` ROS2 Python package

2. ✅ Learned `python-statemachine` library

3. ✅ Designed Vehicle FSM (states & transitions)

4. ✅ Implemented `VehicleFSM` class

5. ✅ Wrote comprehensive unit tests (8 tests, all passing)

 

---

 

## 📚 Key Concepts Learned

 

### 1. Python Package Installation

 

**What is `pip install`?**

- Python's package manager (like an app store for Python code)

- Downloads and installs libraries from the internet

- After installing, you can `import` the library in your code

 

```bash

pip install python-statemachine

```

 

**Editable installs for development:**

```bash

pip install -e src/uav_control/

```

- `-e` = editable mode

- Changes to code take effect immediately (no reinstall needed)

- Required for pytest to find your local packages

 

---

 

### 2. ROS2 Package Types

 

| Build Type | Use Case |

|------------|----------|

| `ament_cmake` | Message packages, C++ code |

| `ament_python` | Python nodes, pure Python packages |

 

**uav_control uses `ament_python`** because we're writing Python nodes.

 

```bash

ros2 pkg create uav_control --build-type ament_python --dependencies rclpy uav_msgs

```

 

---

 

### 3. State Machine Concepts

 

**What is a Finite State Machine (FSM)?**

- A system that can be in exactly ONE state at a time

- Transitions move between states

- Invalid transitions are blocked (safety!)

 

**Key components:**

```

┌─────────────────────────────────────────────────────┐

│                    StateMachine                     │

│                                                     │

│   ┌─────────┐    transition    ┌─────────┐         │

│   │ State A │ ───────────────► │ State B │         │

│   └─────────┘                  └─────────┘         │

│                                                     │

│   - States: distinct modes the system can be in    │

│   - Transitions: named actions that change state   │

│   - Guards: conditions for transitions (future)    │

└─────────────────────────────────────────────────────┘

```

 

---

 

### 4. python-statemachine Library Syntax

 

**Defining states:**

```python

from statemachine import StateMachine, State

 

class MyFSM(StateMachine):

    state_a = State(initial=True)  # Starting state

    state_b = State()

```

 

**Defining transitions:**

```python

# Single transition

go = state_a.to(state_b)

 

# Multiple sources → one destination

land = (hovering | flying).to(landing)

 

# Multiple destinations from one source (use | between full transitions)

flip = off.to(on) | on.to(off)

```

 

**Using the FSM:**

```python

fsm = MyFSM()

print(fsm.current_state.id)  # "state_a"

fsm.go()                      # Transition!

print(fsm.current_state.id)  # "state_b"

```

 

**Handling invalid transitions:**

```python

from statemachine.exceptions import TransitionNotAllowed

 

try:

    fsm.invalid_transition()

except TransitionNotAllowed:

    print("Blocked!")

```

 

---

 

### 5. FSM Design Process

 

**Step 1: Identify states (what can the system BE?)**

- Think about physical/logical modes

- For drone: disarmed, armed, taking_off, hovering, flying, landing, emergency

 

**Step 2: Identify transitions (what CHANGES state?)**

- Commands: user/system requests action

- Events: sensor data triggers change

 

**Step 3: Draw the diagram**

```

DISARMED → ARMED → TAKING_OFF → HOVERING ←→ FLYING

    ▲                              │           │

    └────────── LANDING ◄──────────┴───────────┘

                   ▲

               EMERGENCY

```

 

**Step 4: List all transitions explicitly**

```

arm:               DISARMED → ARMED

disarm:            ARMED → DISARMED

takeoff:           ARMED → TAKING_OFF

...

```

 

---

 

### 6. Unit Testing with pytest

 

**Test file structure:**

```python

import pytest

from statemachine.exceptions import TransitionNotAllowed

from uav_control.vehicle_fsm import VehicleFSM

 

class TestVehicleFSM:

    def test_something(self):

        """Docstring explains what we're testing."""

        fsm = VehicleFSM()

        assert fsm.current_state.id == "expected"

```

 

**Testing exceptions:**

```python

def test_invalid_transition_blocked(self):

    fsm = VehicleFSM()

    with pytest.raises(TransitionNotAllowed):

        fsm.takeoff()  # Can't takeoff from disarmed!

```

 

**Running tests:**

```bash

pytest src/uav_control/test/test_vehicle_fsm.py -v

```

 

---

 

## 🏗️ What Was Built

 

### Vehicle FSM States

 

| State | Meaning |

|-------|---------|

| `disarmed` | On ground, motors won't spin |

| `armed` | On ground, ready to fly |

| `taking_off` | Ascending to target altitude |

| `hovering` | In air, holding position (passive) |

| `flying` | In air, moving to target (active) |

| `landing` | Descending to ground |

| `emergency` | Something went wrong |

 

### Vehicle FSM Transitions

 

| Transition | From → To |

|------------|-----------|

| `arm` | disarmed → armed |

| `disarm` | armed → disarmed |

| `takeoff` | armed → taking_off |

| `takeoff_complete` | taking_off → hovering |

| `navigate` | hovering → flying |

| `target_reached` | flying → hovering |

| `land` | hovering/flying → landing |

| `trigger_emergency` | (any airborne) → emergency |

| `emergency_land` | emergency → landing |

| `touchdown` | landing → disarmed |

 

### Files Created

 

```

src/uav_control/

├── package.xml

├── setup.py

├── setup.cfg

├── resource/uav_control

├── uav_control/

│   ├── __init__.py

│   └── vehicle_fsm.py      # FSM implementation

└── test/

    └── test_vehicle_fsm.py  # 8 unit tests

```

 

---

 

## 🧪 Test Coverage

 

| Test | Purpose |

|------|---------|

| `test_initial_state_is_disarmed` | FSM starts correctly |

| `test_arm_from_disarmed` | Basic valid transition |

| `test_cannot_takeoff_from_disarmed` | Invalid transition blocked |

| `test_cannot_arm_when_flying` | Invalid transition blocked |

| `test_cannot_arm_when_taking_off` | Invalid transition blocked |

| `test_cannot_land_from_armed` | Invalid transition blocked |

| `test_full_mission_sequence` | Complete happy path |

| `test_emergency_during_flight` | Emergency + recovery path |

 

**Result:** 8 passed in 0.09s ✅

 

---

 

## 💡 Key Insights

 

### 1. FSM = Safety Gatekeeper

 

The state machine prevents invalid operations:

- Can't takeoff when disarmed

- Can't arm while flying

- Can't land from ground

 

**For a drone, this is critical safety logic!**

 

### 2. Flight Phase vs Control Mode

 

These are DIFFERENT concepts:

- **Flight phase:** What the drone is physically doing (our FSM)

- **Control mode:** Who/what is controlling it (attribute, not state)

 

A drone can be "hovering" + "guided mode" or "hovering" + "manual mode".

 

### 3. Design Before Code

 

Spending time on FSM design (states, transitions, diagram) made implementation trivial. The code almost wrote itself.

 

### 4. Tests Document Behavior

 

Tests serve two purposes:

- Verify correctness now

- Document expected behavior for future-you

 

---

 

## 🔧 Commands Reference

 

```bash

# Create Python ROS2 package

ros2 pkg create uav_control --build-type ament_python --dependencies rclpy uav_msgs

 

# Install package in editable mode (required for tests)

pip install -e src/uav_control/

 

# Run tests

pytest src/uav_control/test/test_vehicle_fsm.py -v

 

# Run specific test

pytest src/uav_control/test/test_vehicle_fsm.py::TestVehicleFSM::test_arm_from_disarmed -v

```

 

---

 

## 🚀 What's Next

 

### Immediate (Next Session)

 

**VehicleStateNode (Lifecycle Node):**

- Wrap FSM in a ROS2 node

- Subscribe to `/mavros/state`

- Publish `/vehicle/state` using our VehicleState message

- Services for state transitions

 

### Week 2 Remaining

 

- Vehicle Controller node

- Takeoff/Land/Hold actions

- Integration with SITL

 

---

 

## 📊 Session Stats

 

- **Concepts learned:** 6+ major concepts

- **Files created:** 4 files

- **Tests written:** 8 tests

- **Commits made:** 2

- **Bugs encountered:** 0 (clean implementation!)

 

---

 

## ✅ Self-Assessment

 

**Can I now:**

 

1. ✅ Create a ROS2 Python package? YES

2. ✅ Use python-statemachine library? YES

3. ✅ Design an FSM from requirements? YES

4. ✅ Implement an FSM in Python? YES

5. ✅ Write unit tests with pytest? YES

6. ✅ Test both valid and invalid transitions? YES

 

**Confidence level:** 9/10 - Ready for ROS2 node integration!

 

---

 

**Achievement unlocked:** 🎮 **State Machine Architect**

 

**Session vibe:** "This is actually really fun man"

 

---

 

## 📝 Personal Notes

 

### What Worked Well

- Hands-on experimentation before design

- Drawing state diagram before coding

- Testing invalid transitions (not just happy path)

 

### What Was Challenging

- Initially confusing syntax (REPL + indentation)

- Understanding when to use `|` operator

 

### What Surprised Me

- How clean the statemachine library syntax is

- FSM blocks invalid operations automatically (safety!)

- Tests run in 0.09 seconds (fast feedback)

 

---

 

**Status:** Week 2 Day 3-4 COMPLETE! 💪

 

Ready to wrap FSM in a ROS2 node next session!