# MissionStatus.msg - Mission execution status

std_msgs/Header header

# Mission ID (string)
string mission_id

# Current phase (string) - e.g., "TAKEOFF", "SEARCH", "APPROACH"
string current_phase

# Current behavior tree node name (string)
string current_behavior_node

# Progress percentage (float, 0-100)
float32 progress_percentage

# List of active warnings (string array)
string[] active_warnings
