# ================================================================
#  Module      : detector.py — Surveillance Detection Engine
#  Project     : AI-Powered Surveillance System
#  University  : GSCWU Bahawalpur | Dept. of CS & IT
#  Supervisor  : Dr. Amna Ikram
#  Students    : Fatima Majeed (BSCS1FA22-1057)
#                Fatima-tul-Zahra (BSCS1FA22-1051)
#  Description : Loads YOLOv5s model, runs person detection,
#                draws bounding boxes, checks ROI zone intrusion.
# ================================================================

import torch
import cv2
import sys
import os

class SurveillanceDetector:
    def __init__(self, confidence=0.5):
        """Load YOLOv5s model on CPU"""
        self.confidence = confidence
        print("Loading YOLOv5 model...")
        self.model = torch.hub.load(
            'ultralytics/yolov5', 'yolov5s',
            pretrained=True, device='cpu', verbose=False
        )
        self.model.conf = confidence
        self.model.classes = [0]  # Person class only
        print("✅ Model loaded successfully!")

    def detect(self, frame):
        """Run detection on a single frame"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(rgb, size=640)
        return results

    def get_boxes(self, results):
        """Extract bounding boxes as a list of dicts"""
        boxes = []
        for *xyxy, conf, cls in results.xyxy[0].tolist():
            boxes.append({
                'x1': int(xyxy[0]), 'y1': int(xyxy[1]),
                'x2': int(xyxy[2]), 'y2': int(xyxy[3]),
                'confidence': round(conf, 2)
            })
        return boxes

    def draw_boxes(self, frame, boxes, alert=False):
        """
        Draw bounding boxes on detected humans.
        Colour: GREEN (0, 255, 0) — always, for every detected person.
        """
        color = (0, 255, 0)  # Green — human detected

        for box in boxes:
            # Draw bounding box rectangle
            cv2.rectangle(
                frame,
                (box['x1'], box['y1']),
                (box['x2'], box['y2']),
                color, 2
            )
            # Draw filled label background
            label      = f"Human  {box['confidence']:.0%}"
            (tw, th), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(
                frame,
                (box['x1'], box['y1'] - th - 8),
                (box['x1'] + tw + 4, box['y1']),
                color, -1  # Filled
            )
            # Draw label text in black on green background
            cv2.putText(
                frame, label,
                (box['x1'] + 2, box['y1'] - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2
            )

        return frame

    def is_in_zone(self, box, zone):
        """
        Check if detected person's centre point is inside the ROI zone.
        zone = (x1, y1, x2, y2)
        Returns True if inside, False otherwise.
        """
        cx = (box['x1'] + box['x2']) // 2
        cy = (box['y1'] + box['y2']) // 2
        zx1, zy1, zx2, zy2 = zone
        return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

    def draw_zone(self, frame, zone, triggered=False):
        """
        Draw the restricted ROI zone rectangle on the frame.
        Colour: RED (0, 0, 255) — always, whenever video is playing.
        """
        color = (0, 0, 255)  # Red — restricted zone always
        zx1, zy1, zx2, zy2 = zone

        # Draw semi-transparent filled zone overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), color, -1)
        cv2.addWeighted(overlay, 0.08, frame, 0.92, 0, frame)

        # Draw solid border
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), color, 2)

        # Draw corner markers for professional look
        corner_len = 20
        thickness  = 3
        # Top-left
        cv2.line(frame, (zx1, zy1), (zx1 + corner_len, zy1), color, thickness)
        cv2.line(frame, (zx1, zy1), (zx1, zy1 + corner_len), color, thickness)
        # Top-right
        cv2.line(frame, (zx2, zy1), (zx2 - corner_len, zy1), color, thickness)
        cv2.line(frame, (zx2, zy1), (zx2, zy1 + corner_len), color, thickness)
        # Bottom-left
        cv2.line(frame, (zx1, zy2), (zx1 + corner_len, zy2), color, thickness)
        cv2.line(frame, (zx1, zy2), (zx1, zy2 - corner_len), color, thickness)
        # Bottom-right
        cv2.line(frame, (zx2, zy2), (zx2 - corner_len, zy2), color, thickness)
        cv2.line(frame, (zx2, zy2), (zx2, zy2 - corner_len), color, thickness)

        # Draw label with filled background
        label       = "RESTRICTED ZONE"
        (tw, th), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
        )
        cv2.rectangle(
            frame,
            (zx1, zy1 - th - 10),
            (zx1 + tw + 8, zy1),
            color, -1
        )
        cv2.putText(
            frame, label,
            (zx1 + 4, zy1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
        )

        return frame

    def draw_hud(self, frame, person_count, alert_active=False):
        """
        Draw a HUD (Heads-Up Display) overlay on the frame.
        Shows person count and alert status in top-right corner.
        """
        h, w = frame.shape[:2]

        # Status pill — top right
        status_text  = "⚠ ALERT" if alert_active else "MONITORING"
        status_color = (0, 0, 255) if alert_active else (0, 180, 0)
        cv2.rectangle(frame, (w - 180, 10), (w - 10, 40), status_color, -1)
        cv2.putText(
            frame, status_text,
            (w - 170, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
        )

        # Person count — below status
        count_text = f"Persons: {person_count}"
        cv2.rectangle(frame, (w - 180, 46), (w - 10, 72), (30, 30, 30), -1)
        cv2.putText(
            frame, count_text,
            (w - 170, 65),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2
        )

        return frame