"""
Motion Detector
Uses MOG2 background subtraction to find moving people in the frame.
MOG2 is built into OpenCV — no extra install needed.
"""

import cv2


class MotionDetector:
    def __init__(self):
        # MOG2 = Mixture of Gaussians background model
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300,
            varThreshold=50,
            detectShadows=True
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def detect(self, frame):
        """
        Find moving regions in the frame.
        Returns list of person dicts: {bbox, centroid, area}
        """
        # Get foreground mask (white = moving, black = background)
        mask = self.bg_subtractor.apply(frame)

        # Remove shadow pixels (value 127) — keep only full motion (255)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)

        # Clean up noise
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel, iterations=2)
        mask = cv2.dilate(mask, self.kernel, iterations=3)

        # Find contours (blobs of motion)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        persons = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 3000:   # ignore small blobs
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            # A standing person should be taller than wide
            if h < w * 0.8:
                continue

            # Centroid of the blob
            cx = x + w // 2
            cy = y + h // 2

            persons.append({
                "bbox": (x, y, w, h),
                "centroid": (cx, cy),
                "area": area
            })

        return persons, mask
