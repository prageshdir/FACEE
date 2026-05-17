"""
Face Recognizer Module
Uses the face_recognition library (dlib-based) to encode and match faces.
Supports loading known faces from dataset/known_faces/ and webcam registration.
"""

import os
import pickle
import numpy as np

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("[WARNING] face_recognition not installed. Using fallback mode.")

import cv2


class FaceRecognizer:
    ENCODINGS_FILE = "models/face_encodings.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"
    TOLERANCE = 0.55  # lower = stricter matching

    def __init__(self):
        self.known_encodings = []  # list of 128-d face encodings
        self.known_names = []      # matching person names
        self._load_encodings()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_encodings(self):
        """Load pre-computed encodings from disk if available."""
        if os.path.exists(self.ENCODINGS_FILE):
            with open(self.ENCODINGS_FILE, "rb") as f:
                data = pickle.load(f)
                self.known_encodings = data.get("encodings", [])
                self.known_names = data.get("names", [])
            print(f"[FaceRecognizer] Loaded {len(self.known_names)} known faces from cache.")
        else:
            self._build_encodings_from_dataset()

    def save_encodings(self):
        """Persist encodings to disk."""
        os.makedirs("models", exist_ok=True)
        with open(self.ENCODINGS_FILE, "wb") as f:
            pickle.dump({"encodings": self.known_encodings, "names": self.known_names}, f)
        print(f"[FaceRecognizer] Saved {len(self.known_names)} face encodings.")

    # ------------------------------------------------------------------
    # Dataset loading
    # ------------------------------------------------------------------

    def _build_encodings_from_dataset(self):
        """
        Scan dataset/known_faces/<PersonName>/<image>.jpg and build encodings.
        Folder structure:
            known_faces/
                John_Doe/
                    photo1.jpg
                    photo2.jpg
                Jane_Smith/
                    photo1.jpg
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return
        if not os.path.exists(self.KNOWN_FACES_DIR):
            os.makedirs(self.KNOWN_FACES_DIR, exist_ok=True)
            return

        print("[FaceRecognizer] Building face encodings from dataset...")
        count = 0
        for person_name in os.listdir(self.KNOWN_FACES_DIR):
            person_dir = os.path.join(self.KNOWN_FACES_DIR, person_name)
            if not os.path.isdir(person_dir):
                continue
            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img_path = os.path.join(person_dir, img_file)
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(person_name)
                    count += 1
        print(f"[FaceRecognizer] Encoded {count} images for {len(set(self.known_names))} persons.")
        if count > 0:
            self.save_encodings()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_face(self, frame, name):
        """
        Register a new face from a BGR frame captured via webcam.
        Saves the image and updates encodings in real-time.
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return False, "face_recognition library not available."

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            return False, "No face detected in the frame."

        # Save image
        person_dir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(person_dir, exist_ok=True)
        img_count = len(os.listdir(person_dir)) + 1
        img_path = os.path.join(person_dir, f"{name}_{img_count:03d}.jpg")
        cv2.imwrite(img_path, frame)

        self.known_encodings.append(encodings[0])
        self.known_names.append(name)
        self.save_encodings()
        return True, f"Registered {name} successfully."

    # ------------------------------------------------------------------
    # Recognition
    # ------------------------------------------------------------------

    def recognize(self, frame, face_locations=None):
        """
        Recognize faces in a BGR frame.
        Returns list of dicts: {name, confidence, location}
        location = (top, right, bottom, left) in CSS order (face_recognition style)
        """
        if not FACE_RECOGNITION_AVAILABLE or not self.known_encodings:
            return []

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations if not provided (faster to pass from detector)
        if face_locations is None:
            face_locations = face_recognition.face_locations(rgb, model="hog")

        if not face_locations:
            return []

        face_encodings = face_recognition.face_encodings(rgb, face_locations)
        results = []

        for encoding, location in zip(face_encodings, face_locations):
            distances = face_recognition.face_distance(self.known_encodings, encoding)
            best_idx = int(np.argmin(distances))
            best_dist = distances[best_idx]
            confidence = round((1 - best_dist) * 100, 1)

            if best_dist <= self.TOLERANCE:
                name = self.known_names[best_idx]
            else:
                name = "Unknown"
                confidence = round(best_dist * 100, 1)  # show distance as "uncertainty"

            results.append({
                "name": name,
                "confidence": confidence,
                "location": location,  # (top, right, bottom, left)
                "distance": float(best_dist),
            })

        return results

    def reload(self):
        """Force reload encodings from disk."""
        self.known_encodings = []
        self.known_names = []
        self._load_encodings()

    @property
    def known_person_count(self):
        return len(set(self.known_names))
