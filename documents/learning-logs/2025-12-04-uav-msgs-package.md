# Learning Log: Creating First ROS2 Message Package

 

**Date:** 2025-12-04

**Session:** Week 2 Day 2 - Package Creation & Message Generation

**Duration:** ~4-5 hours

**Status:** ✅ Complete Success - First package built and verified!

 

---

 

## 🎯 Session Objectives Achieved

 

By the end of this session, I successfully:

1. ✅ Created my first ROS2 package from scratch (`uav_msgs`)

2. ✅ Wrote 6 custom message definitions

3. ✅ Configured package.xml with proper dependencies

4. ✅ Configured CMakeLists.txt for message generation

5. ✅ Built the package successfully (after debugging!)

6. ✅ Verified messages are importable in Python

7. ✅ Understood multi-language code generation

 

---

 

## 📚 What Was Created

 

### Package Structure

```

uav_msgs/

├── CMakeLists.txt           # Build configuration

├── package.xml              # Package metadata & dependencies

├── msg/                     # Message definitions

│   ├── VehicleState.msg

│   ├── DetectedTarget.msg

│   ├── DetectedTargetArray.msg

│   ├── MissionStatus.msg

│   ├── SafetyStatus.msg

│   └── TrackedTarget.msg

├── src/                     # C++ source (empty for message packages)

└── include/                 # C++ headers (empty for message packages)

```

 

### Generated Output (after build)

```

install/uav_msgs/

├── lib/                     # Shared libraries (.so files)

├── include/                 # C++ headers (.hpp files) - 6 files

├── local/lib/python3.10/    # Python modules (.py files) - 7 files

└── share/                   # Package metadata

```

 

---

 

## 🏗️ Step-by-Step Process

 

### Step 1: Understanding Package Configuration Files

 

**Key Learning:** Explored `std_msgs` package to understand structure

 

**Commands used:**

```bash

ros2 pkg prefix std_msgs

cd /opt/ros/humble/share/std_msgs

cat package.xml

```

 

**Discovery:** Found three types of dependencies:

- `<buildtool_depend>` - Tools needed to BUILD the package

- `<build_depend>` - Packages needed during compilation

- `<exec_depend>` - Packages needed at runtime

- `<depend>` - Shorthand for both build_depend AND exec_depend

 

---

 

### Step 2: Package Naming Decision

 

**Original plan:** `autonomous_uav_msgs`

**Decision:** Changed to `uav_msgs`

 

**Reasoning:**

- Everything in project is autonomous (redundant prefix)

- Cleaner, follows ROS2 conventions (std_msgs, sensor_msgs)

- Specific enough (UAV domain)

- Easy to refactor if expanding to other vehicle types

 

**Naming pattern for all packages:**

- `uav_msgs` - Message definitions

- `uav_control` - Control layer

- `uav_perception` - Perception layer

- `uav_mission` - Mission layer

- `uav_bringup` - Launch files

 

---

 

### Step 3: Creating the Package

 

**Command:**

```bash

cd /ws/src

ros2 pkg create uav_msgs --build-type ament_cmake --dependencies std_msgs geometry_msgs

```

 

**Why `ament_cmake`?**

- Message generation REQUIRES CMake build type

- Cannot use `ament_python` for message packages

- Even though we'll use messages in Python, generation is done by CMake

 

**Generated automatically:**

- package.xml (with dependencies)

- CMakeLists.txt (basic structure)

- src/ and include/ directories

 

---

 

### Step 4: Configuring package.xml

 

**Added three critical lines for message packages:**

 

```xml

<buildtool_depend>rosidl_default_generators</buildtool_depend>

<exec_depend>rosidl_default_runtime</exec_depend>

<member_of_group>rosidl_interface_packages</member_of_group>

```

 

**Why each is needed:**

1. `rosidl_default_generators` - Generates code from .msg files (build time only)

2. `rosidl_default_runtime` - Deserializes messages (runtime only)

3. `member_of_group` - Declares "I'm a message package" to ROS2 build system

 

**Final package.xml structure:**

```xml

<?xml version="1.0"?>

<package format="3">

  <name>uav_msgs</name>

  <version>0.0.0</version>

  <description>Custom ROS2 message definitions for UAV platform</description>

  <maintainer email="root@todo.todo">root</maintainer>

  <license>MIT</license>

 

  <buildtool_depend>ament_cmake</buildtool_depend>

  <buildtool_depend>rosidl_default_generators</buildtool_depend>

 

  <depend>std_msgs</depend>

  <depend>geometry_msgs</depend>

 

  <exec_depend>rosidl_default_runtime</exec_depend>

 

  <test_depend>ament_lint_auto</test_depend>

  <test_depend>ament_lint_common</test_depend>

 

  <member_of_group>rosidl_interface_packages</member_of_group>

 

  <export>

    <build_type>ament_cmake</build_type>

  </export>

</package>

```

 

---

 

### Step 5: Writing Message Definitions

 

#### Message 1: VehicleState.msg

 

**Purpose:** Complete vehicle state for FSM and world model

 

**Key Design Decisions:**

- Used `PoseStamped` (not `Pose`) for frame + timestamp

- Used `TwistStamped` (not `Twist`) for velocity with frame

- Named field `is_guided` (ArduPilot terminology, not PX4's `is_offboard`)

- 7 FSM states defined as uint8 constants

 

**Final design:**

```python

# VehicleState.msg

std_msgs/Header header

uint8 fsm_state

geometry_msgs/PoseStamped pose

geometry_msgs/TwistStamped velocity

float32 battery_level

bool is_armed

bool is_guided

string[] active_faults

 

uint8 STATE_UNINITIALIZED = 0

uint8 STATE_DISARMED = 1

uint8 STATE_ARMED = 2

uint8 STATE_TAKING_OFF = 3

uint8 STATE_FLYING = 4

uint8 STATE_LANDING = 5

uint8 STATE_LANDED = 6

uint8 STATE_EMERGENCY = 7

```

 

**Important architectural insight:** `is_guided` vs `is_offboard`

- PX4 uses "OFFBOARD" mode

- ArduPilot uses "GUIDED" mode

- Chose `is_guided` because we're using ArduPilot

- Message definitions should match actual hardware terminology

 

---

 

#### Message 2: DetectedTarget.msg

 

**Purpose:** Single frame observation from detector (ArUco or YOLO)

 

**Design for extensibility:**

```python

std_msgs/Header header

string target_id              # "aruco_42", "person_1"

string target_class           # "aruco", "person", "car"

geometry_msgs/PoseStamped pose

float32 confidence            # 0.0 - 1.0

float32[4] bounding_box       # [x, y, w, h] normalized

```

 

**Why `float32[4]` for bounding box?**

- NOT `geometry_msgs/Polygon` (that's for 3D world coordinates)

- Bounding box is 2D image coordinates

- Compact (16 bytes vs 48+ bytes)

- Matches YOLO output format

- Normalized [0.0, 1.0] works for any resolution

 

---

 

#### Message 3: TrackedTarget.msg

 

**Purpose:** Temporal tracking with history (wraps DetectedTarget)

 

**Key Concept: Message Composition**

```python

std_msgs/Header header

DetectedTarget detection        # ← Embedding another message!

int32 track_id

int32 detection_count

float32 time_since_last_seen_sec

float32 tracking_confidence

```

 

**Usage in code:**

```python

msg.detection.target_id       # Access nested fields

msg.detection.pose

msg.track_id                  # Access parent fields

```

 

**Why composition is powerful:**

- Reuse existing definitions

- Clear semantic layering (detection → track)

- Avoid field duplication

- Type safety

 

---

 

#### Message 4: SafetyStatus.msg

 

**Purpose:** Safety analysis (not raw state, but interpretation)

 

**Critical Bug Discovered:** Enum collision!

 

**❌ Original (failed to build):**

```python

uint8 CRITICAL = 2    # Collision!

uint8 CRITICAL = 2    # Duplicate name error

```

 

**✅ Fixed with prefixes:**

```python

uint8 safety_state

uint8 SAFETY_STATE_SAFE = 0

uint8 SAFETY_STATE_WARNING = 1

uint8 SAFETY_STATE_CRITICAL = 2

 

uint8 battery_status

uint8 BATTERY_STATUS_OK = 0

uint8 BATTERY_STATUS_LOW = 1

uint8 BATTERY_STATUS_CRITICAL = 2

 

uint8 geofence_status

uint8 GEOFENCE_INSIDE = 0

uint8 GEOFENCE_APPROACHING_BOUNDARY = 1

uint8 GEOFENCE_VIOLATED = 2

```

 

**Naming pattern learned:** `{FIELD_NAME}_{VALUE}`

 

---

 

#### Architectural Insight: VehicleState vs SafetyStatus

 

**Question I had:** "Why do we need both? They seem similar!"

 

**Answer:** Different abstraction levels!

 

**VehicleState (World Model Layer):**

- Raw state data: "What IS happening"

- `battery_level = 15.2%` (actual value)

- `pose.position.z = 45.0` (45 meters high)

- Published by: `vehicle_state_node`

- Update rate: 20-50 Hz (fast, continuous)

 

**SafetyStatus (Safety Monitor Layer):**

- Safety analysis: "Is this SAFE or DANGEROUS?"

- `battery_status = LOW` (threshold-based: 15.2% < 20%)

- `safety_state = WARNING` (low battery at high altitude!)

- Published by: `safety_monitor_node`

- Update rate: 1-10 Hz (slower analysis)

 

**Data flow:**

```

VehicleState → safety_monitor → SafetyStatus

(measurements)   (analysis)      (judgment)

```

 

**Why this design is good:**

- Single Responsibility Principle

- Testability (can mock VehicleState)

- Flexibility (change thresholds without touching state reporting)

- Different update rates possible

 

---

 

### Step 6: Configuring CMakeLists.txt

 

**Added after find_package lines:**

```cmake

find_package(rosidl_default_generators REQUIRED)

 

rosidl_generate_interfaces(${PROJECT_NAME}

  "msg/VehicleState.msg"

  "msg/DetectedTarget.msg"

  "msg/DetectedTargetArray.msg"

  "msg/MissionStatus.msg"

  "msg/SafetyStatus.msg"

  "msg/TrackedTarget.msg"

  DEPENDENCIES std_msgs geometry_msgs

)

```

 

**Key points:**

- `${PROJECT_NAME}` expands to `uav_msgs` (from line 2)

- Message files in quotes (they're file paths)

- `DEPENDENCIES` must match package.xml

- Must be BEFORE `ament_package()`

 

---

 

### Step 7: Building the Package

 

**First attempt:**

```bash

colcon build --packages-select uav_msgs

```

 

**❌ BUILD FAILED!**

```

ValueError: the constants iterable contains duplicate names: CRITICAL

```

 

**Root cause:** SafetyStatus.msg had duplicate enum constants without prefixes

 

**Solution:** Added prefixes to all enum constants in SafetyStatus.msg

 

**Second attempt:**

```bash

colcon build --packages-select uav_msgs

```

 

**✅ SUCCESS!**

```

Starting >>> uav_msgs

Finished <<< uav_msgs [16.5s]

Summary: 1 package finished [16.7s]

```

 

---

 

### Step 8: Verification

 

**Test 1: Interface List**

```bash

source install/setup.bash

ros2 interface list | grep uav_msgs

```

 

**Result:** ✅ All 6 messages listed

```

uav_msgs/msg/DetectedTarget

uav_msgs/msg/DetectedTargetArray

uav_msgs/msg/MissionStatus

uav_msgs/msg/SafetyStatus

uav_msgs/msg/TrackedTarget

uav_msgs/msg/VehicleState

```

 

---

 

**Test 2: Show Message Definition**

```bash

ros2 interface show uav_msgs/msg/VehicleState

```

 

**Result:** ✅ Full message structure displayed with nested types expanded!

 

**Discovery:** ROS2 expanded all nested types:

- `geometry_msgs/PoseStamped` → showed full `Point` and `Quaternion` structure

- All the way down to individual `float64` fields

- Proves message composition is working

 

---

 

**Test 3: Python Import**

```bash

python3 -c 'from uav_msgs.msg import VehicleState; print("Success: VehicleState imported")'

```

 

**Result:** ✅ Import successful!

 

**Test 4: Import Multiple**

```bash

python3 -c 'from uav_msgs.msg import VehicleState, DetectedTarget, SafetyStatus; print("All imports successful!")'

```

 

**Result:** ✅ All imports working!

 

---

 

## 🎓 Key Concepts Learned

 

### 1. ROS2 Dependency Types

 

| Type | When Needed | Example |

|------|-------------|---------|

| `buildtool_depend` | Tools to build package | ament_cmake, rosidl_default_generators |

| `build_depend` | Compile-time only | C++ headers |

| `exec_depend` | Runtime only | rosidl_default_runtime |

| `depend` | Both build AND runtime | std_msgs, geometry_msgs |

 

**Mental model:**

```

buildtool_depend = Factory tools (assembly line)

build_depend     = Parts during manufacturing

exec_depend      = Parts when driving the car

depend           = Parts needed for both

```

 

---

 

### 2. Message Composition Pattern

 

**Embedding messages inside messages:**

```python

# TrackedTarget embeds DetectedTarget

DetectedTarget detection

 

# Access nested fields

msg.detection.target_id

msg.detection.pose

```

 

**Benefits:**

- Reuse existing message definitions

- Clear semantic relationships

- Avoid duplication

- Type safety enforced by build system

 

---

 

### 3. Enum Naming to Avoid Collisions

 

**Problem:** ROS2 constants are global to the message scope

 

**❌ Wrong:**

```python

uint8 CRITICAL = 2

uint8 CRITICAL = 2    # ERROR: Duplicate!

```

 

**✅ Correct:**

```python

uint8 SAFETY_STATE_CRITICAL = 2

uint8 BATTERY_STATUS_CRITICAL = 2    # No collision!

```

 

**Pattern:** `{FIELD_NAME}_{VALUE}`

 

---

 

### 4. Multi-Language Code Generation

 

**From 6 .msg files, ROS2 generated:**

- 7 Python files (6 messages + `__init__.py`)

- 6 C++ headers (`.hpp`)

- 6 C files (`.c` type support)

- Shared libraries (`.so`)

 

**The magic:**

```

Your .msg file

     ↓

  [Build]

     ↓

  ┌──────────┬──────────┬──────────┐

  │  Python  │   C++    │   C      │

  └──────────┴──────────┴──────────┘

     ↓           ↓          ↓

Python node ↔ C++ node ↔ C node

```

 

**This means:** Python and C++ nodes can communicate seamlessly using the same message types!

 

---

 

### 5. Stamped vs Non-Stamped Types

 

**Wrong:**

```python

geometry_msgs/Pose pose        # No frame, no timestamp

geometry_msgs/Twist velocity   # No frame

```

 

**Correct:**

```python

geometry_msgs/PoseStamped pose        # Includes frame_id + timestamp

geometry_msgs/TwistStamped velocity   # Includes frame_id + timestamp

```

 

**Why it matters:**

- Frame ID tells which coordinate system (body, world, camera)

- Timestamp enables time synchronization

- Essential for TF transformations later

 

---

 

### 6. Message Package Build Type

 

**MUST use `ament_cmake`** (not `ament_python`)

 

**Why?**

- Message generation requires CMake

- rosidl tools are CMake-based

- Python can still USE the messages, but generation is CMake

 

---

 

## 🐛 Challenges Faced & Solutions

 

### Challenge 1: Enum Collision Build Error

 

**Error message:**

```

ValueError: the constants iterable contains duplicate names: CRITICAL

```

 

**Debugging process:**

1. Read error carefully - "duplicate names: CRITICAL"

2. Identified SafetyStatus.msg as likely culprit

3. Searched for all instances of CRITICAL

4. Found multiple enums with same constant name

 

**Solution:** Added prefixes to all enum constants

 

**Time to fix:** ~5 minutes

 

**Learning:** Always prefix enum constants with field name

 

---

 

### Challenge 2: Bash History Expansion with `!`

 

**Error:**

```bash

python3 -c "from uav_msgs.msg import VehicleState; print('✅ Success!')"

bash: !': event not found

```

 

**Cause:** Bash interprets `!` as history expansion

 

**Solution:** Use single quotes instead of double quotes

```bash

python3 -c 'from uav_msgs.msg import VehicleState; print("Success")'

```

 

---

 

### Challenge 3: Understanding VehicleState vs SafetyStatus

 

**Initial confusion:** "These seem to overlap - why both?"

 

**Resolution:** They're at different abstraction levels

- VehicleState = measurements

- SafetyStatus = analysis of measurements

 

**Analogy that helped:**

- VehicleState = Dashboard sensors (speedometer: 95 km/h, fuel: 5L)

- SafetyStatus = Warning lights (⚠️ SPEED WARNING, 🔴 FUEL LOW)

 

---

 

## 💡 Insights & Aha Moments

 

### Insight 1: "Configuration Over Code"

 

By using ROS2's message generation system:

- Write .msg file once

- Get Python, C++, and C code automatically

- No manual serialization/deserialization

- Type safety enforced

 

**Aha moment:** "I'm not writing code - I'm defining interfaces, and ROS2 writes the code for me!"

 

---

 

### Insight 2: "Messages are Contracts"

 

Message definitions are **contracts** between nodes:

- Publisher and subscriber must agree on message structure

- Build system enforces this at compile time

- Breaking changes to messages break dependent packages (good!)

 

---

 

### Insight 3: "Dependency Direction = Stability"

 

```

volatile (changes often)

    ↓

uav_bringup

    ↓

uav_mission

    ↓

uav_control, uav_perception

    ↓

uav_msgs  ← Most stable (foundation)

    ↓

stable (changes rarely)

```

 

**Dependencies point toward stability!**

 

Messages are the foundation - they change least frequently.

 

---

 

### Insight 4: "Flight Controller Terminology Matters"

 

Decision to use `is_guided` vs `is_offboard`:

- PX4 → "OFFBOARD"

- ArduPilot → "GUIDED"

- **Chose `is_guided`** because we're using ArduPilot

- **Lesson:** Be precise about your actual system, not generic

 

---

 

## 📊 What Was Generated

 

### File Counts

 

**Python:**

```bash

ls install/uav_msgs/local/lib/python3.10/dist-packages/uav_msgs/msg/*.py | wc -l

# Output: 7 (6 messages + __init__.py)

```

 

**C++:**

```bash

find install/uav_msgs/include/ -name "*.hpp" | wc -l

# Output: 6

```

 

**C:**

```bash

find install/uav_msgs/ -name "*.c" | wc -l

# Output: 6

```

 

---

 

### Generated File Locations

 

```

install/uav_msgs/

├── include/uav_msgs/uav_msgs/msg/

│   ├── vehicle_state.hpp

│   ├── detected_target.hpp

│   └── ... (4 more)

│

├── lib/

│   ├── libuav_msgs__rosidl_generator_c.so

│   ├── libuav_msgs__rosidl_typesupport_cpp.so

│   └── ... (more .so files)

│

├── local/lib/python3.10/dist-packages/uav_msgs/msg/

│   ├── __init__.py

│   ├── _vehicle_state.py

│   ├── _detected_target.py

│   └── ... (4 more)

│

└── share/uav_msgs/

    ├── package.xml

    ├── msg/

    │   └── ... (original .msg files)

    └── cmake/

```

 

---

 

## 🔧 Commands Reference

 

### Package Creation

```bash

cd /ws/src

ros2 pkg create uav_msgs --build-type ament_cmake --dependencies std_msgs geometry_msgs

```

 

### Building

```bash

cd /ws

colcon build --packages-select uav_msgs

source install/setup.bash

```

 

### Verification

```bash

# List all interfaces

ros2 interface list | grep uav_msgs

 

# Show message definition

ros2 interface show uav_msgs/msg/VehicleState

 

# Test Python import

python3 -c 'from uav_msgs.msg import VehicleState; print("Success!")'

 

# Test multiple imports

python3 -c 'from uav_msgs.msg import VehicleState, DetectedTarget, SafetyStatus; print("All good!")'

```

 

### Rebuilding After Changes

```bash

cd /ws

colcon build --packages-select uav_msgs

source install/setup.bash

```

 

---

 

## 📚 Resources for Further Learning

 

**ROS2 Official Docs:**

- Creating packages: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html

- Custom interfaces: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html

- Message design: https://docs.ros.org/en/humble/Concepts/About-ROS-Interfaces.html

 

**Standard Message Packages:**

- std_msgs: https://github.com/ros2/common_interfaces/tree/humble/std_msgs

- geometry_msgs: https://github.com/ros2/common_interfaces/tree/humble/geometry_msgs

- sensor_msgs: https://github.com/ros2/common_interfaces/tree/humble/sensor_msgs

 

---

 

## ✅ Deliverables

 

### Package Files Created

- ✅ `uav_msgs/package.xml` - Complete with all dependencies

- ✅ `uav_msgs/CMakeLists.txt` - Configured for message generation

- ✅ `uav_msgs/msg/VehicleState.msg` - 7 FSM states

- ✅ `uav_msgs/msg/DetectedTarget.msg` - Multi-detector support

- ✅ `uav_msgs/msg/DetectedTargetArray.msg` - Array wrapper

- ✅ `uav_msgs/msg/MissionStatus.msg` - Mission tracking

- ✅ `uav_msgs/msg/SafetyStatus.msg` - Safety analysis (fixed enum collisions)

- ✅ `uav_msgs/msg/TrackedTarget.msg` - Temporal tracking with composition

 

### Build Verification

- ✅ Package builds successfully

- ✅ All 6 messages registered with ROS2

- ✅ Python imports working

- ✅ C++ headers generated

- ✅ Multi-language support verified

 

---

 

## 🎯 Self-Assessment

 

**Can I now:**

 

1. ✅ **Create a ROS2 package from scratch?** YES - Used ros2 pkg create with correct build type

2. ✅ **Write message definitions?** YES - Created 6 messages with various types

3. ✅ **Configure package.xml?** YES - Added all required dependencies for message packages

4. ✅ **Configure CMakeLists.txt?** YES - Added rosidl_generate_interfaces

5. ✅ **Build a message package?** YES - Successfully built and verified

6. ✅ **Debug build errors?** YES - Fixed enum collision error

7. ✅ **Verify message generation?** YES - Used ros2 interface commands

8. ✅ **Import messages in Python?** YES - Tested successfully

 

**Confidence level:** 9/10 - Ready to create more packages!

 

---

 

## 🚀 What's Next

 

### Immediate Next Steps (Week 2 Continuation)

 

**Session 2: Finite State Machine (FSM) Design**

- Module 2: FSM theory and design

- Study python-statemachine library

- Design Vehicle FSM on paper

- Implement with unit tests

- 7 states: UNINITIALIZED → DISARMED → ARMED → TAKING_OFF → FLYING → LANDING → LANDED → EMERGENCY

 

**Session 3: Vehicle State Node Integration**

- Create `uav_control` package

- Implement Vehicle State Node (Lifecycle Node)

- Subscribe to `/mavros/state`

- Publish `/vehicle/state` using our new VehicleState message!

- Services for state transitions

 

**Session 4-5: Vehicle Controller**

- Implement setpoint streaming (20Hz)

- Create action servers (Takeoff, Land, Hold)

- Test full autonomous cycle in SITL

 

---

 

### Future Packages to Create

 

Following the same pattern:

1. `uav_control` - Control layer (Week 2-3)

2. `uav_perception` - Perception layer (Week 4-5)

3. `uav_mission` - Mission layer (Week 5-6)

4. `uav_bringup` - Launch files (Week 7-8)

 

---

 

## 🎉 Session Summary

 

**Time invested:** ~4-5 hours

**Concepts mastered:** 6+ major concepts

**Files created:** 8 files (6 .msg + 2 config files)

**Bugs fixed:** 1 (enum collision)

**Build attempts:** 2 (1 failure, 1 success)

 

**Achievement unlocked:** 🏗️ **ROS2 Package Creator**

 

**Feeling:** Accomplished and confident! Ready for FSM implementation!

 

---

 

## 📝 Personal Notes

 

### What Worked Well

- Starting with exploration (examining std_msgs) before creating

- Making architectural decisions (naming, VehicleState vs SafetyStatus)

- Debugging the build error systematically

- Verifying at each step

 

### What Was Challenging

- Understanding dependency types initially

- Debugging the enum collision (but solved it!)

- Bash history expansion with `!` (minor)

 

### What Surprised Me

- ROS2 generates code for 3 languages from one .msg file!

- Message composition is so elegant

- The build system catches errors early (good design!)

- How much gets generated automatically

 

### What I'm Proud Of

- Made reasoned architectural decisions (is_guided vs is_offboard)

- Debugged the build error myself

- Created 6 complete, well-designed messages

- Understood the separation between VehicleState and SafetyStatus

 

---

 

**Status:** Week 2 Day 2 COMPLETE! 💪

 

Ready to implement the Vehicle FSM next session! The message foundation is solid and ready to use.