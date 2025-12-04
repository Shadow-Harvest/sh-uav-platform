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
uint8 SAFE=0
uint8 WARNING=1
uint8 CRITICAL=2

# Geofence status constants
uint8 INSIDE=0
uint8 APPROACHING_BOUNDARY=1
uint8 VIOLATED=2

# Battery status constants
uint8 OK=0
uint8 LOW=1
uint8 CRITICAL=2