"""
Face Recognizer
Uses OpenCV LBPH with a preprocessing pipeline tuned for accuracy.

Accuracy improvements:
  1. Face alignment via eye detection — aligns eyes to a canonical horizontal
     position before every train/predict call; LBPH accuracy degrades sharply
     when the same person's face is rotated differently between frames.
  2. CLAHE equalisation — lighting invariance.
  3. LBPH radius=2, neighbors=16 — richer local texture descriptors.
  4. 9-variant augmentation per registration capture — brightness (×4),
     horizontal flip, Gaussian blur, rotation ±5° — gives the model
     enough sample variety from a single webcam frame.
  5. Confidence threshold tightened to 70.
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
    MODEL_FILE  = "models/lbph_model.yml"
    LABELS_FILE = "models/labels.pkl"
    KNOWN_FACES_DIR      = "dataset/known_faces"
    CONFIDENCE_THRESHOLD = 70   # LBPH distance; lower = stricter

    def __init__(self):
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self._eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        # radius=2, neighbors=16 captures richer local texture than default (1, 8)
        self.model = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8
        )
        self.label_map  = {}   # int → name
        self.reverse_map = {}  # name → int
        self.trained = False
        self._load_or_train()

    # ── Preprocessing ────────────────────────────────────────

    def _align_face(self, gray: np.ndarray) -> np.ndarray:
        """
        Rotate the face crop so that the eye line is horizontal.
        Falls back to the original image if eyes cannot be detected.
        """
        h, w = gray.shape[:2]
        eyes = self._eye_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15)
        )
        if len(eyes) < 2:
            return gray   # graceful fallback

        eyes = sorted(eyes, key=lambda e: e[0])   # left → right by x
        (ex1, ey1, ew1, eh1) = eyes[0]
        (ex2, ey2, ew2, eh2) = eyes[1]
        cx1, cy1 = ex1 + ew1 // 2, ey1 + eh1 // 2
        cx2, cy2 = ex2 + ew2 // 2, ey2 + eh2 // 2

        angle = float(np.degrees(np.arctan2(cy2 - cy1, cx2 - cx1)))
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_LINEAR)

    def _preprocess(self, gray_img: np.ndarray) -> np.ndarray:
        """Resize → align → CLAHE."""
        img = cv2.resize(gray_img, (100, 100))
        img = self._align_face(img)
        return self._clahe.apply(img)

    # ── Augmentation ─────────────────────────────────────────

    def _augment(self, img: np.ndarray) -> list:
        """
        Return 9 variants from one captured frame:
          original, 4× brightness/contrast, flip, blur, rotate +5°, rotate −5°
        """
        variants = [img]

        # Brightness / contrast shifts
        for alpha, beta in [(1.3, 20), (0.75, -20), (1.15, 10), (0.85, -10)]:
            v = np.clip(img.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
            variants.append(v)

        # Horizontal flip (handles subtle left/right asymmetry)
        variants.append(cv2.flip(img, 1))

        # Slight blur (simulates focus / distance variation)
        variants.append(cv2.GaussianBlur(img, (3, 3), 0))

        # Small rotations to cover slight head tilt
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        for angle in (-5, 5):
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR)
            variants.append(rotated)

        return variants   # 9 total

    # ── Training ─────────────────────────────────────────────

    def _load_or_train(self):
        if os.path.exists(self.MODEL_FILE) and os.path.exists(self.LABELS_FILE):
            self.model.read(self.MODEL_FILE)
            with open(self.LABELS_FILE, "rb") as f:
                data = pickle.load(f)
                self.label_map   = data["label_map"]
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

            self.label_map[label_id]   = person_name
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
        print(f"[FaceRecognizer] Trained on {len(images)} images "
              f"for {label_id} person(s).")

    def _save_model(self):
        os.makedirs("models", exist_ok=True)
        self.model.save(self.MODEL_FILE)
        with open(self.LABELS_FILE, "wb") as f:
            pickle.dump({"label_map": self.label_map,
                         "reverse_map": self.reverse_map}, f)

    # ── Registration ─────────────────────────────────────────

    def register_face(self, gray_face: np.ndarray, name: str) -> tuple[bool, str]:
        """
        Save a new face and retrain.  Generates 9 augmented variants from
        the single captured frame.  Returns (success, message).
        """
        person_dir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(person_dir, exist_ok=True)

        base_img = cv2.resize(gray_face, (100, 100))
        count = len([f for f in os.listdir(person_dir) if f.endswith(".jpg")])

        for i, img in enumerate(self._augment(base_img)):
            cv2.imwrite(os.path.join(person_dir, f"{name}_{count+i+1:03d}.jpg"), img)

        self.label_map    = {}
        self.reverse_map  = {}
        self.trained      = False
        self._train_from_dataset()
        return True, f"Registered '{name}' ({count + 9} photos total)."

    # ── Recognition ──────────────────────────────────────────

    def predict(self, gray_face: np.ndarray) -> tuple[str, int]:
        """
        Returns (name, confidence_percent) where 100 = perfect, 0 = no match.
        """
        if not self.trained:
            return "Unknown", 0

        face_proc = self._preprocess(gray_face)
        label_id, distance = self.model.predict(face_proc)

        confidence = max(0, int(100 - distance))

        if distance > self.CONFIDENCE_THRESHOLD:
            return "Unknown", confidence

        name = self.label_map.get(label_id, "Unknown")
        return name, confidence

    def reload(self):
        self.label_map   = {}
        self.reverse_map = {}
        self.trained     = False
        self._load_or_train()

    @property
    def person_count(self) -> int:
        return len(self.label_map)
