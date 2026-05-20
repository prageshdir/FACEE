"""
GEI-based Gait Recognizer
Pipeline: HOG(GEI) → L2-norm → PCA → LDA → KNN

Why HOG instead of raw pixels:
  - Raw GEI pixels (16 384 features) capture intensity; scale and lighting
    differences between subjects dominate, hurting classification.
  - HOG (Histogram of Oriented Gradients, 1 764 features) captures gradient
    *structure* — silhouette edges and shape — which is invariant to uniform
    lighting and small pixel-level noise from the MOG2 background subtractor.
  - On CASIA-B, HOG-GEI with PCA+LDA consistently outperforms raw-GEI by
    10–20 percentage points at Rank-1.

Pipeline (train):
  1. HOG on each 128×128 GEI  → 1 764-D vector
  2. L2 normalise
  3. PCA to ≥95% variance (capped at min(N-1, 100))
  4. LDA to n_classes-1 axes  (skipped when n_samples ≤ n_classes)
  5. KNN k=3, distance-weighted, Euclidean

Pipeline (predict):
  Same HOG → L2-norm → PCA.transform → LDA.transform → KNN.predict
"""

import os
import pickle
from collections import defaultdict

import cv2
import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize

GEI_H = 128
GEI_W = 128
MODEL_FILE      = "models/gait_model.pkl"
MODEL_VERSION   = 3          # bump whenever the feature pipeline changes
MIN_SILHOUETTES = 25
REFRESH_EVERY   = 10

# Module-level HOG descriptor — instantiated once, reused everywhere
_HOG = cv2.HOGDescriptor(
    _winSize=(GEI_W, GEI_H),
    _blockSize=(32, 32),
    _blockStride=(16, 16),
    _cellSize=(16, 16),
    _nbins=9,
)   # → 1 764-D descriptor


class GaitRecognizer:
    def __init__(self):
        self.pca: PCA | None                         = None
        self.lda: LinearDiscriminantAnalysis | None  = None
        self.knn: KNeighborsClassifier | None        = None
        self.label_map: dict[int, str]               = {}
        self.trained = False
        self._buffers: dict[int, list]               = defaultdict(list)
        self._cache:   dict[int, tuple[str, int]]    = {}
        self._last_n:  dict[int, int]                = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────

    def _load(self):
        if not os.path.exists(MODEL_FILE):
            return
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
        if data.get("version", 0) != MODEL_VERSION:
            print("[GaitRecognizer] Saved model is from an older version — "
                  "please retrain with build_gait_gallery.py")
            return
        self.pca       = data["pca"]
        self.lda       = data["lda"]
        self.knn       = data["knn"]
        self.label_map = data["label_map"]
        self.trained   = True
        print(f"[GaitRecognizer] Loaded model — {len(self.label_map)} subject(s).")

    def save(self):
        os.makedirs("models", exist_ok=True)
        with open(MODEL_FILE, "wb") as f:
            pickle.dump({
                "version":   MODEL_VERSION,
                "pca":       self.pca,
                "lda":       self.lda,
                "knn":       self.knn,
                "label_map": self.label_map,
            }, f)
        print(f"[GaitRecognizer] Model saved → {MODEL_FILE}")

    # ── Feature extraction ───────────────────────────────────

    @staticmethod
    def extract_features(flat_gei: np.ndarray) -> np.ndarray:
        """
        HOG descriptor on a flattened 128×128 GEI.
        Returns a 1 764-D float32 vector.
        """
        gei_u8 = (flat_gei.reshape(GEI_H, GEI_W) * 255).astype(np.uint8)
        # Equalise contrast so gradient magnitudes are comparable across subjects
        gei_eq = cv2.equalizeHist(gei_u8)
        return _HOG.compute(gei_eq).flatten().astype(np.float32)

    # ── Training ─────────────────────────────────────────────

    def train(self, X_gallery: np.ndarray, y_gallery: np.ndarray,
              pca_components: int | None = None):
        """
        Train HOG → L2-norm → PCA → LDA → KNN.

        Args:
            X_gallery     : (N, H*W) float32 — flattened raw GEIs
            y_gallery     : (N,) array of string subject labels
            pca_components: override auto PCA component count
        """
        n_samples = X_gallery.shape[0]
        n_classes = len(set(str(y) for y in y_gallery))

        # ── Step 1: HOG ──
        print("[GaitRecognizer] Extracting HOG features …")
        X_hog = np.vstack([self.extract_features(x) for x in X_gallery])
        print(f"  HOG feature size: {X_hog.shape[1]}")

        # ── Step 2: L2 normalise ──
        X_norm = normalize(X_hog, norm="l2")

        # ── Step 3: PCA ──
        if pca_components is None:
            pca_probe   = PCA(whiten=True).fit(X_norm)
            cum_var     = np.cumsum(pca_probe.explained_variance_ratio_)
            n_pca       = int(np.searchsorted(cum_var, 0.95)) + 1
            n_pca       = min(n_pca, n_samples - 1, 100)
        else:
            n_pca = min(pca_components, n_samples - 1)

        self.pca = PCA(n_components=n_pca, whiten=True)
        X_pca    = self.pca.fit_transform(X_norm)
        print(f"  PCA: {X_hog.shape[1]}D → {n_pca}D  "
              f"({self.pca.explained_variance_ratio_.sum()*100:.1f}% variance)")

        # ── Step 4: LDA (requires n_samples > n_classes) ──
        unique        = sorted(set(str(y) for y in y_gallery))
        self.label_map = {i: name for i, name in enumerate(unique)}
        rev            = {name: i for i, name in self.label_map.items()}
        y_int          = np.array([rev[str(y)] for y in y_gallery])

        if n_samples > n_classes and n_pca >= n_classes - 1:
            n_lda    = min(n_classes - 1, n_pca)
            self.lda = LinearDiscriminantAnalysis(n_components=n_lda)
            X_fit    = self.lda.fit_transform(X_pca, y_int)
            print(f"  LDA: {n_pca}D → {n_lda}D  ({n_classes}-class separability)")
        else:
            self.lda = None
            X_fit    = X_pca
            print(f"  LDA skipped — using PCA features directly")

        # ── Step 5: KNN ──
        k = max(1, min(3, n_samples // n_classes))
        self.knn = KNeighborsClassifier(
            n_neighbors=k, metric="euclidean", weights="distance")
        self.knn.fit(X_fit, y_int)
        print(f"  KNN k={k}")

        self.trained = True
        self.save()
        print(f"[GaitRecognizer] Done — {n_classes} subject(s).")

    # ── GEI helpers ──────────────────────────────────────────

    @staticmethod
    def compute_gei(silhouettes: list) -> np.ndarray | None:
        if not silhouettes:
            return None
        return np.mean(np.stack(silhouettes, axis=0), axis=0)

    @staticmethod
    def crop_silhouette(mask: np.ndarray, bbox: tuple) -> np.ndarray:
        x, y, w, h = bbox
        fh, fw     = mask.shape[:2]
        x1, y1     = max(0, x),     max(0, y)
        x2, y2     = min(fw, x + w), min(fh, y + h)
        crop       = mask[y1:y2, x1:x2]
        if crop.size == 0:
            return np.zeros((GEI_H, GEI_W), dtype=np.float32)
        resized = cv2.resize(crop, (GEI_W, GEI_H), interpolation=cv2.INTER_LINEAR)
        return resized.astype(np.float32) / 255.0

    # ── Live prediction ──────────────────────────────────────

    def add_silhouette(self, track_id: int, sil: np.ndarray):
        self._buffers[track_id].append(sil)

    def predict_track(self, track_id: int) -> tuple[str | None, int]:
        if not self.trained:
            return None, 0

        buf = self._buffers.get(track_id, [])
        n   = len(buf)
        if n < MIN_SILHOUETTES:
            return None, 0

        if n < self._last_n.get(track_id, 0) + REFRESH_EVERY \
                and track_id in self._cache:
            return self._cache[track_id]

        gei = self.compute_gei(buf)
        if gei is None:
            return None, 0

        feat     = self.extract_features(gei.flatten())
        feat_n   = normalize(feat.reshape(1, -1), norm="l2")
        feat_pca = self.pca.transform(feat_n)
        feat_lda = self.lda.transform(feat_pca) if self.lda is not None else feat_pca

        label_int = int(self.knn.predict(feat_lda)[0])
        dist      = float(self.knn.kneighbors(feat_lda)[0][0][0])

        name = self.label_map.get(label_int, "Unknown")
        conf = max(0, min(100, int(100 - dist * 1.5)))

        self._last_n[track_id] = n
        self._cache[track_id]  = (name, conf)
        return name, conf

    def remove_track(self, track_id: int):
        self._buffers.pop(track_id, None)
        self._cache.pop(track_id,   None)
        self._last_n.pop(track_id,  None)

    @property
    def person_count(self) -> int:
        return len(self.label_map)
