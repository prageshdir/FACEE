"""
Motion Detector Module
Uses background subtraction (MOG2) to detect moving persons in video.
Returns contours of moving regions for further gait analysis.
"""

import cv2
import numpy as np


class MotionDetector:
    def __init__(self, history=200, var_threshold=50, detect_shadows=True):
        # MOG2 background subtractor — good balance of speed vs accuracy
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history,
            varThreshold=var_threshold,
            detectShadows=detect_shadows,
        )
        # Morphological kernel to clean noise
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.min_area = 3000  # ignore small blobs (noise)

    def get_foreground_mask(self, frame):
        """Return cleaned binary mask of moving objects."""
        fg_mask = self.bg_subtractor.apply(frame)
        # Remove shadows (gray pixels set to 0)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        # Morphological opening to remove noise, then dilation to fill gaps
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
        fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)
        return fg_mask

    def detect_persons(self, frame):
        """
        Detect moving person regions.
        Returns list of dicts: {bbox, area, contour, centroid}
        bbox = (x, y, w, h)
        """
        fg_mask = self.get_foreground_mask(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        persons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            # Basic aspect ratio filter: a standing person is taller than wide
            aspect = h / (w + 1e-5)
            if aspect < 0.8:
                continue
            M = cv2.moments(cnt)
            cx = int(M["m10"] / (M["m00"] + 1e-5))
            cy = int(M["m01"] / (M["m00"] + 1e-5))
            persons.append({
                "bbox": (x, y, w, h),
                "area": area,
                "contour": cnt,
                "centroid": (cx, cy),
            })

        return persons, fg_mask

    def draw_person_boxes(self, frame, persons, color=(255, 165, 0)):
        """Draw orange bounding boxes around detected persons."""
        for p in persons:
            x, y, w, h = p["bbox"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        return frame
