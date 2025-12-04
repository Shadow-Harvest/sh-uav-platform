# Represents Vehicle State information

# Header
std_msgs/Header header

# FSM State (DISARMED, ARMED, TAKEOFF, LANDING, HOVERING, CRUISING, ...)
uint8 fsm_state

# Position
geometry_msgs/PoseStamped pose

# Velocity
geometry_msgs/TwistStamped velocity

# Battery level (percentage 0.0 - 100.0)
float32 battery_level

# Status flags
bool is_armed
bool is_guided

# Faults
string[] active_faults

# FSM state constants
uint8 STATE_UNINITIALIZED = 0
uint8 STATE_DISARMED = 1
uint8 STATE_ARMED = 2
uint8 STATE_TAKING_OFF = 3
uint8 STATE_FLYING = 4
uint8 STATE_LANDING = 5
uint8 STATE_LANDED = 6
uint8 STATE_EMERGENCY = 7