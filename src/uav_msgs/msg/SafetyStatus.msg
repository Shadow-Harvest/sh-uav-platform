# SafetyStatus.msg - Safety monitoring information

std_msgs/Header header

# Overall safety state (enum: SAFE, WARNING, CRITICAL)
uint8 safety_state

# List of active faults (string array)
string[] active_faults

# Geofence status (enum: INSIDE, APPROACHING_BOUNDARY, VIOLATED)
uint8 geofence_status

# Battery status (enum: OK, LOW, CRITICAL)
uint8 battery_status

# Is emergency landing active?
bool emergency_landing_is_active

# Overall safety state constants
uint8 SAFETY_STATE_SAFE = 0
uint8 SAFETY_STATE_WARNING = 1
uint8 SAFETY_STATE_CRITICAL = 2

# Geofence status constants
uint8 GEOFENCE_STATUS_INSIDE = 0
uint8 GEOFENCE_STATUS_APPROACHING_BOUNDARY = 1
uint8 GEOFENCE_STATUS_VIOLATED = 2

# Battery status constants
uint8 BATTERY_STATUS_OK = 0
uint8 BATTERY_STATUS_LOW = 1
uint8 BATTERY_STATUS_CRITICAL = 2