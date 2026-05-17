"""
Face Detector Module
Uses OpenCV Haar Cascade for fast face detection in video frames.
"""

import cv2
import numpy as np


class FaceDetector:
    def __init__(self):
        # Load Haar Cascade classifier (bundled with OpenCV - no download needed)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )

    def detect_faces(self, frame):
        """
        Detect faces in a frame.
        Returns list of (x, y, w, h) bounding boxes.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(40, 40),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(faces) == 0:
            return []
        return faces.tolist()

    def crop_face(self, frame, bbox, padding=20):
        """Crop and return a face ROI with optional padding."""
        x, y, w, h = bbox
        h_frame, w_frame = frame.shape[:2]
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w_frame, x + w + padding)
        y2 = min(h_frame, y + h + padding)
        return frame[y1:y2, x1:x2]

    def draw_detection_box(self, frame, bbox, color=(0, 255, 0), thickness=2):
        """Draw a rectangle around detected face."""
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame
