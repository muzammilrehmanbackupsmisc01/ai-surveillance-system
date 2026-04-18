# ================================================================
#  AI-Powered Surveillance System for Theft Detection
#  & Criminal Identification
# ================================================================
#  University  : The Government Sadiq College Women University
#                Bahawalpur, Pakistan
#  Department  : Computer Science & Information Technology
#  Program     : BS Computer Science
#  Supervisor  : Dr. Amna Ikram
# ----------------------------------------------------------------
#  Students:
#    1. Fatima Majeed        | BSCS1FA22-1057
#    2. Fatima-tul-Zahra     | BSCS1FA22-1051
# ----------------------------------------------------------------
#  Email       : fatima.majeed941@gmail.com
#  Contact     : 0349 7671270
#  GitHub      : https://github.com/muzammilrehmanbackupsmisc01/
#                ai-surveillance-system
#  Version     : 1.0.0
#  Date        : April 2026
# ================================================================

# ── Project Identity ──────────────────────────────────────────
PROJECT_NAME   = "AI-Powered Surveillance System"
PROJECT_TITLE  = "Theft Detection & Criminal Identification"
VERSION        = "1.0.0"
RELEASE_DATE   = "April 2026"

# ── University Info ───────────────────────────────────────────
UNIVERSITY     = "Govt. Sadiq College Women University Bahawalpur"
DEPARTMENT     = "Department of Computer Science & IT"
PROGRAM        = "BS Computer Science"
SUPERVISOR     = "Dr. Amna Ikram"

# ── Students ─────────────────────────────────────────────────
STUDENTS = [
    {"name": "Fatima Majeed",    "reg": "BSCS1FA22-1057"},
    {"name": "Fatima-tul-Zahra", "reg": "BSCS1FA22-1051"},
]
GROUP_LEAD_EMAIL   = "fatima.majeed941@gmail.com"
GROUP_LEAD_CONTACT = "0349 7671270"
GITHUB_URL         = "https://github.com/muzammilrehmanbackupsmisc01/ai-surveillance-system"

# ── Paths ─────────────────────────────────────────────────────
SNAPSHOT_DIR = "data/snapshots"
VIDEO_DIR    = "data/test_videos"
DB_PATH      = "logs/detections.db"
LOG_PATH     = "logs/system.log"
MODEL_PATH   = "yolov5s.pt"

# ── Detection Defaults ────────────────────────────────────────
DEFAULT_CONFIDENCE  = 0.55
DEFAULT_COOLDOWN    = 10
DEFAULT_SKIP_FRAMES = 3
DEFAULT_FRAME_SIZE  = 640

# ── Default ROI Zone (% of frame) ─────────────────────────────
DEFAULT_ROI = {"x1": 20, "y1": 20, "x2": 80, "y2": 80}

# ── Alert Settings ────────────────────────────────────────────
ALARM_FREQUENCY = 1000   # Hz
ALARM_DURATION  = 300    # milliseconds
ALARM_REPEATS   = 3