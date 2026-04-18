# ─────────────────────────────────────────
# config.py — Central settings for the
# AI Surveillance System
# ─────────────────────────────────────────

# Project info
PROJECT_NAME    = "AI-Powered Surveillance System"
VERSION         = "1.0.0"
UNIVERSITY      = "Govt. Sadiq College Women University Bahawalpur"
DEPARTMENT      = "Department of Computer Science & IT"
SUPERVISOR      = "Dr. Amna Ikram"

# Paths
SNAPSHOT_DIR    = "data/snapshots"
VIDEO_DIR       = "data/test_videos"
DB_PATH         = "logs/detections.db"
LOG_PATH        = "logs/system.log"
MODEL_PATH      = "yolov5s.pt"

# Detection defaults
DEFAULT_CONFIDENCE  = 0.55
DEFAULT_COOLDOWN    = 10
DEFAULT_SKIP_FRAMES = 3
DEFAULT_FRAME_SIZE  = 640

# Default ROI zone (% of frame)
DEFAULT_ROI = {
    "x1": 20,
    "y1": 20,
    "x2": 80,
    "y2": 80
}

# Alert settings
ALARM_FREQUENCY = 1000   # Hz
ALARM_DURATION  = 300    # milliseconds
ALARM_REPEATS   = 3