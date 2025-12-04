# TrackedTarget.msg - Information about a tracked target

# Header
std_msgs/Header header

# Single frame observation of the tracked target
DetectedTarget detection  

# Unique track identifier
int32 track_id

# Number of detections associated with this track
int32 detection_count

# Time since last seen (seconds)
float32 time_since_last_seen_sec

# Tracking confidence (0.0 - 1.0)
float32 tracking_confidence