import torch
import cv2
import sys
import os

class SurveillanceDetector:
    def __init__(self, confidence=0.5):
        """Load YOLOv5 small model on CPU"""
        self.confidence = confidence
        print("Loading YOLOv5 model...")
        self.model = torch.hub.load(
            'ultralytics/yolov5', 'yolov5s',
            pretrained=True, device='cpu', verbose=False
        )
        self.model.conf = confidence
        self.model.classes = [0]  # Only detect 'person' class
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
        """Draw bounding boxes — red if alert, green if normal"""
        color = (0, 0, 255) if alert else (0, 255, 0)
        for box in boxes:
            cv2.rectangle(frame,
                (box['x1'], box['y1']),
                (box['x2'], box['y2']),
                color, 2)
            label = f"Person {box['confidence']:.0%}"
            cv2.putText(frame, label,
                (box['x1'], box['y1'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

    def is_in_zone(self, box, zone):
        """Check if person's center point is inside the ROI zone.
        zone = (x1, y1, x2, y2)"""
        cx = (box['x1'] + box['x2']) // 2
        cy = (box['y1'] + box['y2']) // 2
        zx1, zy1, zx2, zy2 = zone
        return zx1 <= cx <= zx2 and zy1 <= cy <= zy2

    def draw_zone(self, frame, zone, triggered=False):
        """Draw the ROI zone rectangle on the frame"""
        color = (0, 0, 255) if triggered else (255, 165, 0)
        zx1, zy1, zx2, zy2 = zone
        cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), color, 2)
        label = "RESTRICTED ZONE"
        cv2.putText(frame, label, (zx1, zy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame