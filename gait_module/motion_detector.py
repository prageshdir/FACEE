"""
Motion Detector
Uses MOG2 background subtraction to find moving people in the frame.
MOG2 is built into OpenCV — no extra install needed.

Improvements over baseline:
  - Longer history (500 frames) → more stable background model
  - Lower varThreshold (40) → detects slower/subtler motion
  - Extra closing pass fills holes inside silhouettes so the blob
    is a solid mask rather than a hollow shell — this gives the
    gait analyzer more accurate area and height measurements.
"""

import cv2


class MotionDetector:
    def __init__(self):
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=40,
            detectShadows=True
        )
        self._open_kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self._close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT,    (9, 9))

    def detect(self, frame):
        """
        Find moving regions in the frame.
        Returns list of person dicts: {bbox, centroid, area}, plus the binary mask.
        """
        mask = self.bg_subtractor.apply(frame)

        # Remove shadow pixels (127) — keep only full motion (255)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)

        # Open: remove small noise speckles
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  self._open_kernel,  iterations=2)
        # Close: fill holes inside the person silhouette
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self._close_kernel, iterations=2)
        # Dilate: merge nearby fragments into one person blob
        mask = cv2.dilate(mask, self._open_kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        persons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 2500:   # skip small blobs (noise / partial detections)
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            # A standing/walking person is taller than wide
            if h < w * 0.7:
                continue

            cx = x + w // 2
            cy = y + h // 2

            persons.append({
                "bbox":     (x, y, w, h),
                "centroid": (cx, cy),
                "area":     area,
            })

        return persons, mask
