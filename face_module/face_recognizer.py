"""
Face Recognizer — LBPH + FisherFaces ensemble with multi-frame registration.

Accuracy stack:
  1. Face alignment (eye-level rotation) — consistent spatial layout for LBPH.
  2. CLAHE preprocessing — lighting invariance.
  3. LBPH (radius=2, neighbors=16) — robust local texture descriptor.
  4. FisherFaces — uses PCA+LDA internally; maximises between-person
     discriminability, same principle applied to face space as our gait LDA.
  5. Ensemble vote — both models predict independently; agreement raises
     confidence, disagreement signals "Unknown".
  6. Multi-frame registration — caller supplies N face crops; each crop
     gets 9 augmented variants → N×9 training images from one session.
     Typical: 5 captures × 9 = 45 images per person instead of 9.
"""

import os
import cv2
import numpy as np
import pickle

if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
    raise ImportError(
        "\n[ERROR] cv2.face module not found.\n"
        "Fix: pip uninstall opencv-python opencv-contrib-python && "
        "pip install opencv-contrib-python==4.10.0.84\n"
    )


class FaceRecognizer:
    MODEL_FILE   = "models/lbph_model.yml"
    FISHER_FILE  = "models/fisher_model.yml"
    LABELS_FILE  = "models/labels.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"

    # LBPH: distance < this → known face  (0=perfect, 100+=bad)
    LBPH_THRESHOLD   = 70
    # FisherFaces: distance < this → known face (scale is much larger)
    FISHER_THRESHOLD = 8000

    def __init__(self):
        self._clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self._eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        self._lbph   = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8
        )
        self._fisher = cv2.face.FisherFaceRecognizer_create()

        self.label_map   = {}   # int → name
        self.reverse_map = {}   # name → int
        self.trained     = False
        self._fisher_ok  = False   # FisherFaces needs ≥2 classes

        self._load_or_train()

    # ── Preprocessing ─────────────────────────────────────────

    def _align_face(self, gray: np.ndarray) -> np.ndarray:
        """Rotate so the two eyes are horizontal. Falls back silently."""
        eyes = self._eye_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(15, 15)
        )
        if len(eyes) < 2:
            return gray
        eyes  = sorted(eyes, key=lambda e: e[0])
        cx1   = eyes[0][0] + eyes[0][2] // 2
        cy1   = eyes[0][1] + eyes[0][3] // 2
        cx2   = eyes[1][0] + eyes[1][2] // 2
        cy2   = eyes[1][1] + eyes[1][3] // 2
        angle = float(np.degrees(np.arctan2(cy2 - cy1, cx2 - cx1)))
        h, w  = gray.shape[:2]
        M     = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_LINEAR)

    def _preprocess(self, gray_img: np.ndarray) -> np.ndarray:
        """Resize → align → CLAHE. Returns 100×100 uint8."""
        img = cv2.resize(gray_img, (100, 100))
        img = self._align_face(img)
        return self._clahe.apply(img)

    # ── Augmentation ──────────────────────────────────────────

    def _augment(self, img: np.ndarray) -> list[np.ndarray]:
        """9 variants: original, 4×brightness, flip, blur, rotate ±5°."""
        variants = [img]
        for alpha, beta in [(1.3, 20), (0.75, -20), (1.15, 10), (0.85, -10)]:
            v = np.clip(img.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
            variants.append(v)
        variants.append(cv2.flip(img, 1))
        variants.append(cv2.GaussianBlur(img, (3, 3), 0))
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        for angle in (-5, 5):
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            variants.append(cv2.warpAffine(img, M, (w, h)))
        return variants   # 9 total

    # ── Training ──────────────────────────────────────────────

    def _load_or_train(self):
        if (os.path.exists(self.MODEL_FILE) and
                os.path.exists(self.LABELS_FILE)):
            self._lbph.read(self.MODEL_FILE)
            with open(self.LABELS_FILE, "rb") as f:
                data = pickle.load(f)
            self.label_map   = data["label_map"]
            self.reverse_map = data["reverse_map"]
            if os.path.exists(self.FISHER_FILE) and len(self.label_map) >= 2:
                self._fisher.read(self.FISHER_FILE)
                self._fisher_ok = True
            self.trained = len(self.label_map) > 0
            print(f"[FaceRecognizer] Loaded — {len(self.label_map)} person(s)"
                  f"  (Fisher: {'✓' if self._fisher_ok else '✗ needs ≥2 people'})")
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
            self.label_map[label_id]      = person_name
            self.reverse_map[person_name] = label_id

            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(
                    os.path.join(person_dir, img_file), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                images.append(self._preprocess(img))
                labels.append(label_id)

            label_id += 1

        if not images:
            print("[FaceRecognizer] No training images found.")
            return

        y = np.array(labels)
        self._lbph.train(images, y)

        # FisherFaces needs ≥2 classes
        if label_id >= 2:
            self._fisher.train(images, y)
            self._save_fisher()
            self._fisher_ok = True
        else:
            self._fisher_ok = False

        self._save_model()
        self.trained = True
        print(f"[FaceRecognizer] Trained on {len(images)} images "
              f"for {label_id} person(s)  "
              f"(Fisher: {'✓' if self._fisher_ok else '✗ needs ≥2 people'})")

    def _save_model(self):
        os.makedirs("models", exist_ok=True)
        self._lbph.save(self.MODEL_FILE)
        with open(self.LABELS_FILE, "wb") as f:
            pickle.dump({"label_map":   self.label_map,
                         "reverse_map": self.reverse_map}, f)

    def _save_fisher(self):
        os.makedirs("models", exist_ok=True)
        self._fisher.save(self.FISHER_FILE)

    # ── Registration ──────────────────────────────────────────

    def register_face(self, gray_face: np.ndarray, name: str) -> tuple[bool, str]:
        """Single-frame registration (9 augments). Used by legacy callers."""
        return self.register_multiple([gray_face], name)

    def register_multiple(self, gray_faces: list[np.ndarray],
                          name: str) -> tuple[bool, str]:
        """
        Register from multiple captured frames.
        Each frame → preprocess → 9 augments → save to disk.
        5 frames → 45 training images per person.
        """
        person_dir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(person_dir, exist_ok=True)

        count = len([f for f in os.listdir(person_dir) if f.endswith(".jpg")])
        saved = 0
        for face in gray_faces:
            base = self._preprocess(face)
            for img in self._augment(base):
                cv2.imwrite(
                    os.path.join(person_dir, f"{name}_{count+saved+1:03d}.jpg"),
                    img)
                saved += 1

        self.label_map    = {}
        self.reverse_map  = {}
        self._fisher_ok   = False
        self.trained      = False
        self._train_from_dataset()
        total = count + saved
        return True, f"Registered '{name}' — {total} photos total ({saved} new)."

    # ── Recognition ───────────────────────────────────────────

    def predict(self, gray_face: np.ndarray) -> tuple[str, int]:
        """
        LBPH + FisherFaces ensemble.
        Returns (name, confidence_percent) — 100=perfect, 0=no match.

        Decision logic:
          Both agree and both within threshold → high confidence
          Only LBPH within threshold           → moderate confidence
          Neither within threshold             → Unknown
        """
        if not self.trained:
            return "Unknown", 0

        face_proc = self._preprocess(gray_face)

        lbph_id,   lbph_dist   = self._lbph.predict(face_proc)
        lbph_name = self.label_map.get(lbph_id, "Unknown")
        lbph_conf = max(0, int(100 - lbph_dist))

        # FisherFaces ensemble (only when ≥2 people trained)
        if self._fisher_ok:
            fisher_id,  fisher_dist = self._fisher.predict(face_proc)
            fisher_name = self.label_map.get(fisher_id, "Unknown")

            both_known = (lbph_dist   <= self.LBPH_THRESHOLD and
                          fisher_dist <= self.FISHER_THRESHOLD)
            agree      = lbph_name == fisher_name

            if both_known and agree:
                # Strong agreement: boost confidence slightly
                conf = min(100, lbph_conf + 10)
                return lbph_name, conf
            if both_known and not agree:
                # Conflict: be conservative
                return "Unknown", max(0, lbph_conf - 20)
            if lbph_dist <= self.LBPH_THRESHOLD:
                return lbph_name, lbph_conf
            return "Unknown", lbph_conf

        # LBPH only (single person or first registration)
        if lbph_dist > self.LBPH_THRESHOLD:
            return "Unknown", lbph_conf
        return lbph_name, lbph_conf

    def reload(self):
        self.label_map    = {}
        self.reverse_map  = {}
        self._fisher_ok   = False
        self.trained      = False
        self._load_or_train()

    @property
    def person_count(self) -> int:
        return len(self.label_map)
