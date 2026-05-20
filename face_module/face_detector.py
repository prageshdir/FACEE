"""
Face Detector
Uses OpenCV Haar Cascade - built into OpenCV, no extra download needed.
"""

import cv2


class FaceDetector:
    def __init__(self):
        # alt2 is the most accurate frontal-face cascade shipped with OpenCV
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        )
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def detect(self, frame):
        """
        Find faces in a frame.
        Returns list of (x, y, w, h) boxes.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # CLAHE equalisation makes detection robust to lighting changes
        gray = self._clahe.apply(gray)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,   # finer scale steps → catches more faces
            minNeighbors=4,     # slightly permissive; LBPH still filters by confidence
            minSize=(40, 40)
        )
        if len(faces) == 0:
            return []
        return faces.tolist()
