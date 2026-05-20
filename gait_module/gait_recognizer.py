"""
GEI-based Gait Recognizer
Implements the algorithm from the gait recognition notebook:
  1. Accumulate silhouette frames per person track
  2. Compute GEI (Gait Energy Image) = average of all frames
  3. PCA for dimensionality reduction
  4. KNN (k=1, Euclidean) for identity matching

The model is trained offline via build_gait_gallery.py and saved to
models/gait_model.pkl.  At runtime the live MOG2 silhouettes are
collected per track, a GEI is computed once MIN_SILHOUETTES are
available, and the nearest gallery GEI is returned.
"""

import os
import pickle
from collections import defaultdict

import cv2
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier

GEI_H = 128
GEI_W = 128
MODEL_FILE = "models/gait_model.pkl"
MIN_SILHOUETTES = 25   # frames needed before predicting
REFRESH_EVERY   = 10   # re-predict every N new frames after the first


class GaitRecognizer:
    def __init__(self):
        self.pca: PCA | None = None
        self.knn: KNeighborsClassifier | None = None
        self.label_map: dict[int, str] = {}   # int → name/id
        self.trained = False
        # Per-track buffers: track_id → list of (H, W) float32 silhouettes
        self._buffers: dict[int, list] = defaultdict(list)
        # Cache last prediction per track
        self._cache: dict[int, tuple[str, int]] = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────

    def _load(self):
        if not os.path.exists(MODEL_FILE):
            return
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
        self.pca       = data["pca"]
        self.knn       = data["knn"]
        self.label_map = data["label_map"]
        self.trained   = True
        print(f"[GaitRecognizer] Loaded model — {len(self.label_map)} subject(s).")

    def save(self):
        os.makedirs("models", exist_ok=True)
        with open(MODEL_FILE, "wb") as f:
            pickle.dump({
                "pca":       self.pca,
                "knn":       self.knn,
                "label_map": self.label_map,
            }, f)
        print(f"[GaitRecognizer] Model saved → {MODEL_FILE}")

    # ── Training ─────────────────────────────────────────────

    def train(self, X_gallery: np.ndarray, y_gallery: np.ndarray,
              n_components: int | None = None):
        """
        Train PCA + KNN from pre-computed gallery GEI vectors.

        Args:
            X_gallery : (N, H*W) float32 — flattened GEI per subject
            y_gallery : (N,) str/int   — subject labels
            n_components: PCA dims; defaults to min(N-1, 20)
        """
        n_max = min(X_gallery.shape[0] - 1, X_gallery.shape[1])
        if n_components is None:
            n_components = min(n_max, 20)
        else:
            n_components = min(n_components, n_max)

        print(f"[GaitRecognizer] Training PCA({n_components}) + KNN on "
              f"{X_gallery.shape[0]} gallery GEIs …")

        self.pca = PCA(n_components=n_components, whiten=True)
        X_pca = self.pca.fit_transform(X_gallery)

        # Map string labels → ints for sklearn
        unique = sorted(set(str(y) for y in y_gallery))
        self.label_map = {i: name for i, name in enumerate(unique)}
        rev = {name: i for i, name in self.label_map.items()}
        y_int = np.array([rev[str(y)] for y in y_gallery])

        self.knn = KNeighborsClassifier(n_neighbors=1, metric="euclidean")
        self.knn.fit(X_pca, y_int)
        self.trained = True
        self.save()
        print(f"[GaitRecognizer] Training complete — {len(unique)} subject(s).")

    # ── GEI helpers ──────────────────────────────────────────

    @staticmethod
    def compute_gei(silhouettes: list) -> np.ndarray | None:
        """Average a list of (H, W) float32 masks into a GEI."""
        if not silhouettes:
            return None
        stacked = np.stack(silhouettes, axis=0)  # (N, H, W)
        return np.mean(stacked, axis=0)           # (H, W)

    @staticmethod
    def crop_silhouette(mask: np.ndarray, bbox: tuple) -> np.ndarray:
        """
        Crop a person's region from the binary MOG2 mask and resize to GEI_H×GEI_W.
        Returns float32 image in [0, 1].
        """
        x, y, w, h = bbox
        # Clamp to frame bounds
        fh, fw = mask.shape[:2]
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(fw, x + w), min(fh, y + h)
        crop = mask[y1:y2, x1:x2]
        if crop.size == 0:
            return np.zeros((GEI_H, GEI_W), dtype=np.float32)
        resized = cv2.resize(crop, (GEI_W, GEI_H), interpolation=cv2.INTER_LINEAR)
        return resized.astype(np.float32) / 255.0

    # ── Live prediction ──────────────────────────────────────

    def add_silhouette(self, track_id: int, sil: np.ndarray):
        """Accumulate one silhouette frame for the given track."""
        self._buffers[track_id].append(sil)

    def predict_track(self, track_id: int) -> tuple[str | None, int]:
        """
        Return (identity, confidence%) for a track once enough frames
        are buffered; re-evaluates every REFRESH_EVERY new frames.
        Returns (None, 0) if not enough data or model not trained.
        """
        if not self.trained:
            return None, 0

        buf = self._buffers.get(track_id, [])
        n = len(buf)

        if n < MIN_SILHOUETTES:
            return None, 0

        # Only recompute when new frames arrived
        last_computed = getattr(self, "_last_n", {}).get(track_id, 0)
        if n < last_computed + REFRESH_EVERY and track_id in self._cache:
            return self._cache[track_id]

        gei = self.compute_gei(buf)
        if gei is None:
            return None, 0

        gei_vec = gei.flatten().reshape(1, -1)
        gei_pca = self.pca.transform(gei_vec)

        label_int = int(self.knn.predict(gei_pca)[0])
        dist = float(self.knn.kneighbors(gei_pca)[0][0][0])

        name = self.label_map.get(label_int, "Unknown")
        # Rough confidence: distance ≈ 0 → 100%, distance ≈ 50+ → 0%
        conf = max(0, min(100, int(100 - dist * 2)))

        if not hasattr(self, "_last_n"):
            self._last_n = {}
        self._last_n[track_id] = n
        self._cache[track_id] = (name, conf)
        return name, conf

    def remove_track(self, track_id: int):
        """Call when a track disappears to free its buffer."""
        self._buffers.pop(track_id, None)
        self._cache.pop(track_id, None)
        if hasattr(self, "_last_n"):
            self._last_n.pop(track_id, None)

    @property
    def person_count(self) -> int:
        return len(self.label_map)
