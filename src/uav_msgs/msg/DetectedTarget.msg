# One frame's observation of DetectedTarget.msg

std_msgs/Header header

# Unique ID for this detected target
string target_id         

# Target class (string) - e.g., "ARUCO_MARKER", "YOLO"
string target_class

# Confidence score (float, 0.0-1.0)
float32 confidence_score

# 2D bounding box in normalized image coordinates [0.0 - 1.0]
# Format: [x_center, y_center, width, height]
float32[4] bounding_box

# Pose of the detected target
geometry_msgs/PoseStamped pose

