"""
GEI-based Gait Recognizer
Implements GEI + PCA + LDA + KNN, significantly outperforming PCA-only.

Why PCA+LDA beats PCA alone:
  - PCA maximises *variance* — it keeps the directions where data spreads
    the most, regardless of class boundaries.
  - LDA (Fisher's Linear Discriminant) maximises the *ratio of between-class
    to within-class scatter* — the subspace it finds is specifically optimised
    for distinguishing one person from another.
  - On CASIA-B the combination typically doubles Rank-1 accuracy vs PCA-only.

Pipeline (train):
  1. Per-sample L2 normalise the flattened GEI vectors.
  2. PCA: reduce to min(n_subjects-1, 100) components (keeps ≥95% variance).
  3. LDA: project to at most n_subjects-1 discriminant axes.
  4. KNN k=3, Euclidean distance in the LDA space.

Pipeline (predict):
  Same normalise → PCA.transform → LDA.transform → KNN.predict.
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
MODEL_FILE     = "models/gait_model.pkl"
MIN_SILHOUETTES = 25   # frames needed before predicting
REFRESH_EVERY   = 10   # re-predict every N new frames after the first


class GaitRecognizer:
    def __init__(self):
        self.pca: PCA | None                              = None
        self.lda: LinearDiscriminantAnalysis | None       = None
        self.knn: KNeighborsClassifier | None             = None
        self.label_map: dict[int, str]                    = {}
        self.trained = False
        self._buffers: dict[int, list]                    = defaultdict(list)
        self._cache:   dict[int, tuple[str, int]]         = {}
        self._last_n:  dict[int, int]                     = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────

    def _load(self):
        if not os.path.exists(MODEL_FILE):
            return
        with open(MODEL_FILE, "rb") as f:
            data = pickle.load(f)
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
                "pca":       self.pca,
                "lda":       self.lda,
                "knn":       self.knn,
                "label_map": self.label_map,
            }, f)
        print(f"[GaitRecognizer] Model saved → {MODEL_FILE}")

    # ── Training ─────────────────────────────────────────────

    def train(self, X_gallery: np.ndarray, y_gallery: np.ndarray,
              pca_components: int | None = None):
        """
        Train PCA → LDA → KNN pipeline.

        Args:
            X_gallery     : (N, H*W) float32 — flattened GEIs
            y_gallery     : (N,)     — string subject labels
            pca_components: PCA dims before LDA; None = auto (≥95% variance,
                            capped at min(N-1, 100))
        """
        n_samples, n_feat = X_gallery.shape
        n_classes         = len(set(str(y) for y in y_gallery))

        # ── Step 1: L2 normalise each GEI vector ──
        X_norm = normalize(X_gallery, norm="l2")

        # ── Step 2: PCA ──
        if pca_components is None:
            # Keep enough components to explain ≥95% variance
            pca_full = PCA(whiten=True).fit(X_norm)
            cum_var  = np.cumsum(pca_full.explained_variance_ratio_)
            n_pca    = int(np.searchsorted(cum_var, 0.95)) + 1
            n_pca    = min(n_pca, n_samples - 1, 100)
        else:
            n_pca = min(pca_components, n_samples - 1, n_feat)

        self.pca = PCA(n_components=n_pca, whiten=True)
        X_pca    = self.pca.fit_transform(X_norm)

        print(f"[GaitRecognizer] PCA: {n_feat}D → {n_pca}D  "
              f"(explains {self.pca.explained_variance_ratio_.sum()*100:.1f}% variance)")

        # ── Step 3: LDA ──
        # LDA can produce at most n_classes-1 components
        n_lda = min(n_classes - 1, n_pca)

        # Map labels to ints
        unique        = sorted(set(str(y) for y in y_gallery))
        self.label_map = {i: name for i, name in enumerate(unique)}
        rev            = {name: i for i, name in self.label_map.items()}
        y_int          = np.array([rev[str(y)] for y in y_gallery])

        # LDA requires strictly more samples than classes; fall back to PCA-only
        # when there is only 1 gallery GEI per person (single sequence).
        if n_samples > n_classes and n_lda >= 1:
            self.lda = LinearDiscriminantAnalysis(n_components=n_lda)
            X_fit    = self.lda.fit_transform(X_pca, y_int)
            print(f"[GaitRecognizer] LDA: {n_pca}D → {n_lda}D  "
                  f"(maximises {n_classes}-class separability)")
        else:
            self.lda = None
            X_fit    = X_pca
            print(f"[GaitRecognizer] LDA skipped "
                  f"(need more gallery GEIs than subjects; using PCA only)")

        # ── Step 4: KNN ──
        # k=3 with distance weighting is more robust than k=1 at boundaries
        k = min(3, n_samples // n_classes)
        self.knn = KNeighborsClassifier(n_neighbors=max(1, k),
                                        metric="euclidean",
                                        weights="distance")
        self.knn.fit(X_fit, y_int)

        self.trained = True
        self.save()
        print(f"[GaitRecognizer] Training complete — {n_classes} subject(s), "
              f"KNN k={max(1, k)}.")

    # ── GEI helpers ──────────────────────────────────────────

    @staticmethod
    def compute_gei(silhouettes: list) -> np.ndarray | None:
        """Average a list of (H, W) float32 masks into a GEI."""
        if not silhouettes:
            return None
        return np.mean(np.stack(silhouettes, axis=0), axis=0)

    @staticmethod
    def crop_silhouette(mask: np.ndarray, bbox: tuple) -> np.ndarray:
        """
        Crop a person's region from the MOG2 binary mask and resize to
        GEI_H × GEI_W.  Returns float32 in [0, 1].
        """
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
        """
        Return (identity, confidence%) once MIN_SILHOUETTES are buffered.
        Re-evaluates every REFRESH_EVERY new frames.
        Returns (None, 0) if not ready or model not trained.
        """
        if not self.trained:
            return None, 0

        buf = self._buffers.get(track_id, [])
        n   = len(buf)
        if n < MIN_SILHOUETTES:
            return None, 0

        # Reuse cached result unless new frames arrived
        if n < self._last_n.get(track_id, 0) + REFRESH_EVERY \
                and track_id in self._cache:
            return self._cache[track_id]

        gei = self.compute_gei(buf)
        if gei is None:
            return None, 0

        # Apply the same pipeline as training
        vec     = gei.flatten().reshape(1, -1)
        vec_n   = normalize(vec, norm="l2")
        vec_pca = self.pca.transform(vec_n)
        vec_lda = self.lda.transform(vec_pca) if self.lda is not None else vec_pca

        label_int = int(self.knn.predict(vec_lda)[0])
        dist      = float(self.knn.kneighbors(vec_lda)[0][0][0])

        name = self.label_map.get(label_int, "Unknown")
        # Scale confidence: distance 0 → 100%, distance 50+ → ~0%
        conf = max(0, min(100, int(100 - dist * 1.5)))

        self._last_n[track_id]  = n
        self._cache[track_id]   = (name, conf)
        return name, conf

    def remove_track(self, track_id: int):
        self._buffers.pop(track_id, None)
        self._cache.pop(track_id, None)
        self._last_n.pop(track_id, None)

    @property
    def person_count(self) -> int:
        return len(self.label_map)
