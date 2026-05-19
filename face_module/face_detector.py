"""
Face Detector
Uses OpenCV Haar Cascade - built into OpenCV, no extra download needed.
"""

import cv2


class FaceDetector:
    def __init__(self):
        # Haar Cascade is included with OpenCV automatically
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def detect(self, frame):
        """
        Find faces in a frame.
        Returns list of (x, y, w, h) boxes.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        if len(faces) == 0:
            return []
        return faces.tolist()
