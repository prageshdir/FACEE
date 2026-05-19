"""
Face Recognizer
Uses OpenCV LBPH (Local Binary Pattern Histograms).
No dlib, no cmake, no build tools — works out of the box with OpenCV.
"""

import os
import cv2
import numpy as np
import pickle

if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
    raise ImportError(
        "\n\n[ERROR] cv2.face.LBPHFaceRecognizer_create not found.\n"
        "This usually means 'opencv-python' and 'opencv-contrib-python' are BOTH installed,\n"
        "causing a conflict, OR only 'opencv-python' is installed.\n\n"
        "Fix:\n"
        "  1. pip uninstall opencv-python opencv-contrib-python\n"
        "  2. pip install opencv-contrib-python\n"
    )


class FaceRecognizer:
    MODEL_FILE = "models/lbph_model.yml"
    LABELS_FILE = "models/labels.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"
    CONFIDENCE_THRESHOLD = 80  # lower = more strict

    def __init__(self):
        # LBPH recognizer is built into opencv-contrib-python
        self.model = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}       # int -> name
        self.reverse_map = {}     # name -> int
        self.trained = False
        self._load_or_train()

    # ── Training ─────────────────────────────────────────────

    def _load_or_train(self):
        """Load saved model or train fresh from dataset/known_faces/."""
        if os.path.exists(self.MODEL_FILE) and os.path.exists(self.LABELS_FILE):
            self.model.read(self.MODEL_FILE)
            with open(self.LABELS_FILE, "rb") as f:
                data = pickle.load(f)
                self.label_map = data["label_map"]
                self.reverse_map = data["reverse_map"]
            self.trained = len(self.label_map) > 0
            print(f"[FaceRecognizer] Loaded model — {len(self.label_map)} person(s).")
        else:
            self._train_from_dataset()

    def _train_from_dataset(self):
        """Scan known_faces/ folder and train LBPH model."""
        faces_dir = self.KNOWN_FACES_DIR
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir, exist_ok=True)
            return

        images = []
        labels = []
        label_id = 0

        for person_name in sorted(os.listdir(faces_dir)):
            person_dir = os.path.join(faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue

            self.label_map[label_id] = person_name
            self.reverse_map[person_name] = label_id

            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img_path = os.path.join(person_dir, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, (100, 100))
                images.append(img)
                labels.append(label_id)

            label_id += 1

        if len(images) == 0:
            print("[FaceRecognizer] No training images found.")
            return

        self.model.train(images, np.array(labels))
        self._save_model()
        self.trained = True
        print(f"[FaceRecognizer] Trained on {len(images)} images for {label_id} person(s).")

    def _save_model(self):
        os.makedirs("models", exist_ok=True)
        self.model.save(self.MODEL_FILE)
        with open(self.LABELS_FILE, "wb") as f:
            pickle.dump({"label_map": self.label_map, "reverse_map": self.reverse_map}, f)

    # ── Registration ──────────────────────────────────────────

    def register_face(self, gray_face, name):
        """
        Add a new face (grayscale 100x100 crop) to the database and retrain.
        Returns (success, message).
        """
        person_dir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(person_dir, exist_ok=True)

        count = len([f for f in os.listdir(person_dir) if f.endswith(".jpg")])
        img_path = os.path.join(person_dir, f"{name}_{count + 1:03d}.jpg")
        face_resized = cv2.resize(gray_face, (100, 100))
        cv2.imwrite(img_path, face_resized)

        # Retrain with new data
        self.label_map = {}
        self.reverse_map = {}
        self.trained = False
        self._train_from_dataset()
        return True, f"Registered '{name}' ({count + 1} photo)."

    # ── Recognition ──────────────────────────────────────────

    def predict(self, gray_face):
        """
        Predict who a face belongs to.
        Returns (name, confidence_percent).
        confidence_percent: 100 = perfect match, 0 = no match.
        """
        if not self.trained:
            return "Unknown", 0

        face_resized = cv2.resize(gray_face, (100, 100))
        label_id, distance = self.model.predict(face_resized)

        # LBPH distance: 0 = perfect, >100 = bad. Convert to 0-100% confidence.
        confidence = max(0, int(100 - distance))

        if distance > self.CONFIDENCE_THRESHOLD:
            return "Unknown", confidence

        name = self.label_map.get(label_id, "Unknown")
        return name, confidence

    def reload(self):
        """Reload model from disk."""
        self.label_map = {}
        self.reverse_map = {}
        self.trained = False
        self._load_or_train()

    @property
    def person_count(self):
        return len(self.label_map)
