"""
Gait Analyzer
Classifies gait (Standing / Walking / Running) and, when a trained gallery
model is available, identifies *who* is walking.

Classification uses four motion features (speed, vertical oscillation,
area variation, height variation) as improved in the previous refactor.

Identity recognition uses the GEI + PCA + KNN pipeline from the notebook:
  - Each active track accumulates cropped silhouette frames.
  - Once MIN_SILHOUETTES frames are buffered, a GEI is computed and matched
    against the gallery with KNN in PCA space.
  - The result is shown in the overlay as  "Subject 001 (82%)"  alongside
    the gait label.
"""

from collections import deque

import numpy as np
import time

from .gait_recognizer import GaitRecognizer


class GaitAnalyzer:
    TRAIL_LEN  = 45
    MIN_FRAMES = 15

    def __init__(self):
        # track_id → deque of (cx, cy, timestamp, area, height)
        self.tracks: dict[int, deque] = {}
        self._next_id = 0
        self.recognizer = GaitRecognizer()   # loads saved model if present

    # ── Public API ────────────────────────────────────────────

    def update(self, persons: list, mask=None) -> list:
        """
        Feed current-frame detections.

        Args:
            persons: list of {bbox, centroid, area} dicts from MotionDetector
            mask:    optional binary uint8 mask (same size as frame) — when
                     provided and the gait model is trained, silhouettes are
                     cropped from it for identity recognition.

        Returns list of result dicts:
            {track_id, label, score, bbox, centroid,
             person_id (str|None), person_conf (int)}
        """
        active_ids = set()
        results = []

        for p in persons:
            cx, cy = p["centroid"]
            _, _, w, h = p["bbox"]
            area = p["area"]

            tid = self._get_track(cx, cy)
            self.tracks[tid].append((cx, cy, time.time(), area, h))
            active_ids.add(tid)

            # Gait motion classification
            label, score = self._classify(tid)

            # Identity recognition via GEI (requires mask + trained model)
            person_id, person_conf = None, 0
            if mask is not None and self.recognizer.trained:
                sil = GaitRecognizer.crop_silhouette(mask, p["bbox"])
                self.recognizer.add_silhouette(tid, sil)
                person_id, person_conf = self.recognizer.predict_track(tid)

            results.append({
                "track_id":    tid,
                "label":       label,
                "score":       score,
                "bbox":        p["bbox"],
                "centroid":    (cx, cy),
                "person_id":   person_id,
                "person_conf": person_conf,
            })

        # Prune disappeared tracks
        for tid in list(self.tracks.keys()):
            if tid not in active_ids:
                del self.tracks[tid]
                self.recognizer.remove_track(tid)

        return results

    # ── Internal helpers ──────────────────────────────────────

    def _get_track(self, cx: int, cy: int, max_dist: int = 80) -> int:
        best_id, best_dist = None, float("inf")
        for tid, trail in self.tracks.items():
            if not trail:
                continue
            lx, ly, *_ = trail[-1]
            d = np.hypot(cx - lx, cy - ly)
            if d < best_dist:
                best_dist = d
                best_id = tid
        if best_id is not None and best_dist < max_dist:
            return best_id
        new_id = self._next_id
        self._next_id += 1
        self.tracks[new_id] = deque(maxlen=self.TRAIL_LEN)
        return new_id

    def _classify(self, tid: int) -> tuple[str, int]:
        """Multi-feature gait classification. Returns (label, score%)."""
        trail = list(self.tracks[tid])
        if len(trail) < self.MIN_FRAMES:
            return "Detecting...", 0

        positions = np.array([(x, y) for x, y, *_ in trail])
        areas     = np.array([a       for *_, a, _ in trail])
        heights   = np.array([h       for *_, h    in trail])

        diffs     = np.diff(positions, axis=0)
        distances = np.hypot(diffs[:, 0], diffs[:, 1])
        avg_speed = float(np.mean(distances))

        y_diffs       = np.diff(positions[:, 1])
        y_oscillation = float(np.std(y_diffs))

        area_cv   = float(np.std(areas))   / (float(np.mean(areas))   + 1e-6)
        height_cv = float(np.std(heights)) / (float(np.mean(heights)) + 1e-6)

        motion_score = (
            avg_speed     * 1.0 +
            y_oscillation * 1.5 +
            area_cv       * 30  +
            height_cv     * 20
        )

        if motion_score < 4.0:
            label = "Standing"
            score = min(95, int(90 - motion_score * 5))
        elif motion_score < 18.0:
            label = "Walking"
            score = min(95, int(40 + motion_score * 3))
        else:
            label = "Running"
            score = min(100, int(50 + motion_score * 2))

        return label, max(score, 0)
