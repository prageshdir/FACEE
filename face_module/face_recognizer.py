"""
Face Recognizer
Uses OpenCV LBPH (Local Binary Pattern Histograms) with CLAHE preprocessing.

Accuracy improvements over baseline:
  1. CLAHE (adaptive histogram equalisation) before every train/predict call —
     makes the descriptor lighting-invariant.
  2. Tuned LBPH radius=2, neighbors=16 — captures larger local patterns and
     more gradient directions, reducing confusion between similar faces.
  3. Confidence threshold tightened to 70 — fewer false positives.
  4. Multi-sample registration — every registration call saves 5 augmented
     variants (brightness shifts, minor blur) so a single-frame capture still
     gives the model enough variety to generalise.
"""

import os
import cv2
import numpy as np
import pickle

if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
    raise ImportError(
        "\n\n[ERROR] cv2.face.LBPHFaceRecognizer_create not found.\n"
        "This usually means opencv-contrib-python is missing or the wrong version.\n\n"
        "Fix:\n"
        "  1. pip uninstall opencv-python opencv-contrib-python\n"
        "  2. pip install opencv-contrib-python==4.10.0.84\n"
    )


class FaceRecognizer:
    MODEL_FILE = "models/lbph_model.yml"
    LABELS_FILE = "models/labels.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"
    CONFIDENCE_THRESHOLD = 70   # LBPH distance; lower = stricter

    def __init__(self):
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # radius=2, neighbors=16 captures richer local texture than the default (1, 8)
        self.model = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8
        )
        self.label_map = {}
        self.reverse_map = {}
        self.trained = False
        self._load_or_train()

    # ── Preprocessing ─────────────────────────────────────────

    def _preprocess(self, gray_img):
        """Resize to 100×100 and apply CLAHE for lighting invariance."""
        img = cv2.resize(gray_img, (100, 100))
        return self._clahe.apply(img)

    # ── Training ──────────────────────────────────────────────

    def _load_or_train(self):
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
        faces_dir = self.KNOWN_FACES_DIR
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir, exist_ok=True)
            return

        images, labels = [], []
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
                img = cv2.imread(os.path.join(person_dir, img_file), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                images.append(self._preprocess(img))
                labels.append(label_id)

            label_id += 1

        if not images:
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
        Save a new face and retrain.  Generates 5 augmented variants from the
        single captured frame so the model gets enough sample variety.
        Returns (success, message).
        """
        person_dir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(person_dir, exist_ok=True)

        base_img = cv2.resize(gray_face, (100, 100))
        count = len([f for f in os.listdir(person_dir) if f.endswith(".jpg")])

        # Save original + 4 augmented variants
        augmented = self._augment(base_img)
        for i, img in enumerate(augmented):
            img_path = os.path.join(person_dir, f"{name}_{count + i + 1:03d}.jpg")
            cv2.imwrite(img_path, img)

        self.label_map = {}
        self.reverse_map = {}
        self.trained = False
        self._train_from_dataset()
        return True, f"Registered '{name}' ({count + len(augmented)} photos total)."

    def _augment(self, img):
        """Return original + brightness/contrast variants to cover lighting variation."""
        variants = [img]
        for alpha, beta in [(1.3, 20), (0.75, -20), (1.15, 10), (0.85, -10)]:
            v = np.clip(img.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
            variants.append(v)
        return variants

    # ── Recognition ──────────────────────────────────────────

    def predict(self, gray_face):
        """
        Predict who a face belongs to.
        Returns (name, confidence_percent) where 100 = perfect, 0 = no match.
        """
        if not self.trained:
            return "Unknown", 0

        face_proc = self._preprocess(gray_face)
        label_id, distance = self.model.predict(face_proc)

        # LBPH distance: 0=perfect, >100=bad. Convert to 0–100% confidence.
        confidence = max(0, int(100 - distance))

        if distance > self.CONFIDENCE_THRESHOLD:
            return "Unknown", confidence

        name = self.label_map.get(label_id, "Unknown")
        return name, confidence

    def reload(self):
        self.label_map = {}
        self.reverse_map = {}
        self.trained = False
        self._load_or_train()

    @property
    def person_count(self):
        return len(self.label_map)
