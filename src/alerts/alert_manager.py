# ================================================================
#  Module      : alert_manager.py — Alert & Notification System
#  Project     : AI-Powered Surveillance System
#  University  : GSCWU Bahawalpur | Dept. of CS & IT
#  Supervisor  : Dr. Amna Ikram
#  Students    : Fatima Majeed (BSCS1FA22-1057)
#                Fatima-tul-Zahra (BSCS1FA22-1051)
#  Description : Handles alarm sound, snapshot capture, cooldown,
#                and alert event data generation.
# ================================================================

import cv2
import os
import winsound
from datetime import datetime
import threading

class AlertManager:
    def __init__(self, snapshot_dir="data/snapshots", cooldown_sec=5):
        """Initialize alert manager with snapshot folder and cooldown"""
        self.snapshot_dir = snapshot_dir
        self.cooldown_sec = cooldown_sec
        self.last_alert_time = None
        self.alert_count = 0
        os.makedirs(snapshot_dir, exist_ok=True)
        print("✅ Alert Manager initialized!")

    def can_alert(self):
        """Prevent alarm spam — enforce cooldown between alerts"""
        if self.last_alert_time is None:
            return True
        elapsed = (datetime.now() - self.last_alert_time).seconds
        return elapsed >= self.cooldown_sec

    def trigger_alert(self, frame, zone_name="Zone A", confidence=0.0):
        """Main alert function — call this when intrusion is detected"""
        if not self.can_alert():
            return None

        self.last_alert_time = datetime.now()
        self.alert_count += 1

        # Save snapshot
        snapshot_path = self.save_snapshot(frame)

        # Play alarm sound in background (non-blocking)
        threading.Thread(target=self._play_alarm, daemon=True).start()

        print(f"🚨 ALERT #{self.alert_count} | Zone: {zone_name} | "
              f"Confidence: {confidence:.0%} | Time: {self.last_alert_time.strftime('%H:%M:%S')}")

        return {
            'timestamp': self.last_alert_time.isoformat(),
            'zone': zone_name,
            'confidence': confidence,
            'snapshot_path': snapshot_path
        }

    def save_snapshot(self, frame):
        """Save the alert frame as a timestamped image"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_{ts}.jpg"
        path = os.path.join(self.snapshot_dir, filename)
        cv2.imwrite(path, frame)
        print(f"📸 Snapshot saved: {path}")
        return path

    def _play_alarm(self):
        """Play 3 beeps using Windows built-in sound"""
        for _ in range(3):
            winsound.Beep(1000, 300)  # 1000Hz frequency, 300ms duration