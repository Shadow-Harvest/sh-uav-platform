# Session 08: Target Tracker

**Phase:** 2 - Perception Pipeline
**Estimated Duration:** 3-4 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 07 complete (ArUco detector publishes)
- [ ] Understand low-pass filtering basics
- [ ] Detections visible in /detection/targets

---

## Learning Objectives

By the end of this session, you will understand:

1. **Why tracking is needed** - smoothing, persistence, noise rejection
2. **Simple filtering** - exponential moving average (EMA)
3. **Track management** - creation, update, deletion
4. **Temporal persistence** - handling missed detections

---

## Practical Objectives

### Primary Goal
Implement target tracker that smooths pose estimates and maintains tracks across detection gaps.

### Deliverables

1. **Implement `target_tracker.py`:**
   - Subscribe to `/detection/targets`
   - Maintain track state for each target_id
   - Apply EMA smoothing to pose
   - Publish to `/tracking/targets` (TrackedTarget for each track)

2. **Track lifecycle:**
   - Create track on first detection
   - Update with new measurements (filtered)
   - Maintain for timeout (1s) after last detection
   - Delete after timeout

3. **TrackedTarget message population:**
   - detection: latest (or interpolated) DetectedTarget
   - track_id: unique integer ID
   - detection_count: how many detections
   - time_since_last_seen_sec: freshness
   - tracking_confidence: based on history

4. **Unit tests:**
   - Test track creation on first detection
   - Test smoothing reduces noise
   - Test track persists through gap
   - Test track deleted after timeout

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Design tracker state machine and data structures |
| 0:30-1:15 | Implement Track class with filtering |
| 1:15-1:45 | Implement TargetTracker node |
| 1:45-2:15 | Implement track lifecycle (create/update/delete) |
| 2:15-2:45 | Write unit tests |
| 2:45-3:30 | SITL testing |
| 3:30-4:00 | Commit, document |

---

## Verification Checklist

```bash
# 1. Node runs
ros2 run uav_perception target_tracker

# 2. Tracks published when detector active
ros2 topic echo /tracking/targets

# 3. Verify smoothing
# Compare /detection/targets (jittery) vs /tracking/targets (smooth)
# Use rqt_plot or rosbag + analysis

# 4. Verify persistence
# Briefly block camera, track should persist for 1s
# time_since_last_seen_sec should increase

# 5. Verify deletion
# Remove marker visibility for >1s
# Track should disappear from /tracking/targets
```

---

## Key Questions to Answer During Session

1. What's a good smoothing factor (alpha) for EMA?
2. How long should tracks persist without detections?
3. Should we smooth position only, or also orientation?
4. How to assign track_id for new detections?

---

## Exponential Moving Average (EMA)

```python
class Track:
    def __init__(self, target_id, initial_pose):
        self.target_id = target_id
        self.track_id = self._generate_track_id()
        self.pose = initial_pose
        self.alpha = 0.3  # Smoothing factor (0 = no update, 1 = no smoothing)
        self.detection_count = 1
        self.last_seen = time.time()

    def update(self, new_pose):
        # EMA: smoothed = alpha * new + (1 - alpha) * old
        self.pose.position.x = self.alpha * new_pose.position.x + (1 - self.alpha) * self.pose.position.x
        self.pose.position.y = self.alpha * new_pose.position.y + (1 - self.alpha) * self.pose.position.y
        self.pose.position.z = self.alpha * new_pose.position.z + (1 - self.alpha) * self.pose.position.z
        # ... similar for orientation (use slerp for quaternions)
        self.detection_count += 1
        self.last_seen = time.time()
```

---

## Tracker State Machine

```
Detection received
        │
        ▼
   ┌──────────┐    target_id matches existing track?
   │ Lookup   │────────────────────────────────────────┐
   │ Track    │                                        │
   └──────────┘    NO                                 YES
        │                                              │
        ▼                                              ▼
   ┌──────────┐                                   ┌──────────┐
   │ Create   │                                   │ Update   │
   │ New Track│                                   │ Track    │
   └──────────┘                                   └──────────┘

Timer (10Hz):
   ┌──────────┐
   │ Check    │ ─── time_since_last_seen > 1.0s ──► Delete Track
   │ Timeout  │
   └──────────┘
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| No tracks published | Empty output | Check subscription working |
| Tracks oscillate | Position jumps | Reduce alpha (more smoothing) |
| Tracks never deleted | Old tracks linger | Check timeout logic |
| Quaternion issues | Orientation flips | Use slerp for quaternion filtering |
| Multiple tracks same marker | ID mismatch | Check target_id matching |

---

## Code Locations

- Tracker: `src/uav_perception/uav_perception/target_tracker.py`
- Tests: `src/uav_perception/test/test_target_tracker.py`

---

## Tuning Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| alpha | 0.3 | EMA smoothing (lower = smoother) |
| timeout_sec | 1.0 | Time before track deletion |
| min_detections | 3 | Detections before "confirmed" |
| publish_rate | 10 | Hz for track publishing |

---

## Definition of Done

- [ ] target_tracker node implemented
- [ ] Subscribes to /detection/targets
- [ ] Publishes /tracking/targets (TrackedTarget)
- [ ] EMA smoothing applied to pose
- [ ] Tracks persist through 1s gaps
- [ ] Tracks deleted after timeout
- [ ] At least 3 unit tests
- [ ] SITL: smooth tracks visible when hovering over marker
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 09 will integrate the full perception pipeline and verify end-to-end operation: camera → detector → tracker → verified poses.
