"""
Face Recognizer — SFace CNN (OpenCV DNN).
Extracts 128-dim face embeddings with a CNN; matches via cosine similarity.
Falls back to LBPH if the model cannot be downloaded.
"""

import os
import cv2
import numpy as np
import pickle
import urllib.request


_SFACE_URL  = ("https://media.githubusercontent.com/media/opencv/opencv_zoo"
               "/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx")
_SFACE_PATH = "models/face_recognition_sface_2021dec.onnx"
_MIN_BYTES  = 500_000   # real model is ~37 MB; LFS pointer is ~130 bytes

_COSINE_THRESH = 0.363   # SFace recommended threshold (higher = more confident)
_LBPH_THRESH   = 80      # LBPH distance threshold (lower = stricter)


def _try_download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        print("[FaceRecognizer] Downloading SFace CNN model (~37 MB)…")
        urllib.request.urlretrieve(url, path)
        if os.path.getsize(path) < _MIN_BYTES:
            os.remove(path)
            return False
        print("[FaceRecognizer] SFace model ready.")
        return True
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        print(f"[FaceRecognizer] Download failed ({e}). Using LBPH fallback.")
        return False


# ── CNN backend ───────────────────────────────────────────────

class _SFaceBackend:
    EMBEDDINGS_FILE = "models/face_embeddings.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"

    def __init__(self):
        self._sfr = cv2.FaceRecognizerSF.create(_SFACE_PATH, "")
        self._db = {}   # name -> list of embedding arrays
        self._load()

    def _embed(self, gray_or_bgr):
        if len(gray_or_bgr.shape) == 2:
            img = cv2.cvtColor(gray_or_bgr, cv2.COLOR_GRAY2BGR)
        else:
            img = gray_or_bgr
        img = cv2.resize(img, (112, 112))
        return self._sfr.feature(img)

    def _load(self):
        if os.path.exists(self.EMBEDDINGS_FILE):
            with open(self.EMBEDDINGS_FILE, "rb") as f:
                self._db = pickle.load(f)
            print(f"[FaceRecognizer/CNN] Loaded {len(self._db)} person(s).")
        else:
            self._build_from_dataset()

    def _build_from_dataset(self):
        d = self.KNOWN_FACES_DIR
        if not os.path.isdir(d):
            return
        for name in sorted(os.listdir(d)):
            pdir = os.path.join(d, name)
            if not os.path.isdir(pdir):
                continue
            embs = []
            for fname in sorted(os.listdir(pdir)):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(os.path.join(pdir, fname), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    embs.append(self._embed(img))
            if embs:
                self._db[name] = embs
        self._save()

    def _save(self):
        os.makedirs("models", exist_ok=True)
        with open(self.EMBEDDINGS_FILE, "wb") as f:
            pickle.dump(self._db, f)

    # ── Public interface ──────────────────────────────────────

    def predict(self, gray_face):
        if not self._db:
            return "Unknown", 0
        q = self._embed(gray_face)
        best_name, best_score = "Unknown", 0.0
        for name, embs in self._db.items():
            for emb in embs:
                score = float(self._sfr.match(
                    q, emb, cv2.FaceRecognizerSF_FR_COSINE))
                if score > best_score:
                    best_score, best_name = score, name
        confidence = int(best_score * 100)
        if best_score < _COSINE_THRESH:
            return "Unknown", confidence
        return best_name, confidence

    def register_face(self, gray_face, name):
        pdir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(pdir, exist_ok=True)
        count = len([f for f in os.listdir(pdir) if f.endswith(".jpg")])
        cv2.imwrite(os.path.join(pdir, f"{name}_{count+1:03d}.jpg"),
                    cv2.resize(gray_face, (100, 100)))
        emb = self._embed(gray_face)
        self._db.setdefault(name, []).append(emb)
        self._save()
        return True, f"Registered '{name}' ({count+1} photo)."

    def reload(self):
        self._db = {}
        self._load()

    @property
    def trained(self):
        return bool(self._db)

    @property
    def person_count(self):
        return len(self._db)


# ── LBPH fallback ─────────────────────────────────────────────

class _LBPHBackend:
    MODEL_FILE  = "models/lbph_model.yml"
    LABELS_FILE = "models/labels.pkl"
    KNOWN_FACES_DIR = "dataset/known_faces"

    def __init__(self):
        self.model     = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}
        self.reverse_map = {}
        self.trained   = False
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.MODEL_FILE) and os.path.exists(self.LABELS_FILE):
            self.model.read(self.MODEL_FILE)
            with open(self.LABELS_FILE, "rb") as f:
                d = pickle.load(f)
                self.label_map   = d["label_map"]
                self.reverse_map = d["reverse_map"]
            self.trained = bool(self.label_map)
        else:
            self._train_from_dataset()

    def _train_from_dataset(self):
        d = self.KNOWN_FACES_DIR
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            return
        images, labels, lid = [], [], 0
        for name in sorted(os.listdir(d)):
            pdir = os.path.join(d, name)
            if not os.path.isdir(pdir):
                continue
            self.label_map[lid]   = name
            self.reverse_map[name] = lid
            for fn in os.listdir(pdir):
                if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                img = cv2.imread(os.path.join(pdir, fn), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    images.append(cv2.resize(img, (100, 100)))
                    labels.append(lid)
            lid += 1
        if not images:
            return
        self.model.train(images, np.array(labels))
        self._save()
        self.trained = True

    def _save(self):
        os.makedirs("models", exist_ok=True)
        self.model.save(self.MODEL_FILE)
        with open(self.LABELS_FILE, "wb") as f:
            pickle.dump({"label_map": self.label_map,
                         "reverse_map": self.reverse_map}, f)

    def predict(self, gray_face):
        if not self.trained:
            return "Unknown", 0
        face = cv2.resize(gray_face, (100, 100))
        lid, dist = self.model.predict(face)
        conf = max(0, int(100 - dist))
        if dist > _LBPH_THRESH:
            return "Unknown", conf
        return self.label_map.get(lid, "Unknown"), conf

    def register_face(self, gray_face, name):
        pdir = os.path.join(self.KNOWN_FACES_DIR, name)
        os.makedirs(pdir, exist_ok=True)
        count = len([f for f in os.listdir(pdir) if f.endswith(".jpg")])
        cv2.imwrite(os.path.join(pdir, f"{name}_{count+1:03d}.jpg"),
                    cv2.resize(gray_face, (100, 100)))
        self.label_map   = {}
        self.reverse_map = {}
        self.trained     = False
        self._train_from_dataset()
        return True, f"Registered '{name}' ({count+1} photo)."

    def reload(self):
        self.label_map   = {}
        self.reverse_map = {}
        self.trained     = False
        self._load_or_train()

    @property
    def person_count(self):
        return len(self.label_map)


# ── Public wrapper (same interface as before) ─────────────────

class FaceRecognizer:
    def __init__(self):
        if os.path.exists(_SFACE_PATH) and os.path.getsize(_SFACE_PATH) >= _MIN_BYTES:
            use_cnn = True
        else:
            use_cnn = _try_download(_SFACE_URL, _SFACE_PATH)

        if use_cnn:
            print("[FaceRecognizer] Using SFace CNN backend.")
            self._backend = _SFaceBackend()
        else:
            print("[FaceRecognizer] Using LBPH fallback backend.")
            self._backend = _LBPHBackend()

    @property
    def backend(self):
        return ("SFace CNN" if isinstance(self._backend, _SFaceBackend)
                else "LBPH (fallback)")

    def predict(self, gray_face):
        return self._backend.predict(gray_face)

    def register_face(self, gray_face, name):
        return self._backend.register_face(gray_face, name)

    def reload(self):
        self._backend.reload()

    @property
    def trained(self):
        return self._backend.trained

    @property
    def person_count(self):
        return self._backend.person_count
