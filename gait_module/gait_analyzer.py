"""
Gait Analyzer
Classifies gait (Standing / Walking / Running) from a centroid + silhouette trail.

Improvements over the speed-only baseline, inspired by the GEI notebook approach:

  1. Multi-feature classification:
       • avg_speed      — overall centroid displacement per frame
       • y_oscillation  — std-dev of frame-to-frame vertical displacement;
                          walking/running produce a regular up-down bounce
       • area_cv        — coefficient of variation of blob area; high for
                          running (limbs flail) and near-zero for standing
       • height_cv      — coefficient of variation of bounding-box height;
                          captures limb swing that changes silhouette height

  2. Longer trail (45 frames) and higher MIN_FRAMES (15) give the classifier
     more temporal context before emitting a label.

  3. Weighted scoring combines all four features rather than relying on a
     single speed threshold — mirrors the GEI idea of building a single
     descriptor from many frames.
"""

from collections import deque
import numpy as np
import time


class GaitAnalyzer:
    TRAIL_LEN  = 45   # frames of history per track
    MIN_FRAMES = 15   # minimum frames before classifying

    def __init__(self):
        # track_id → deque of (cx, cy, timestamp, area, height)
        self.tracks: dict[int, deque] = {}
        self._next_id = 0

    # ── Public API ────────────────────────────────────────────

    def update(self, persons):
        """
        Feed current-frame detections.
        Returns list of result dicts: {track_id, label, score, bbox, centroid}.
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

            label, score = self._classify(tid)
            results.append({
                "track_id": tid,
                "label":    label,
                "score":    score,
                "bbox":     p["bbox"],
                "centroid": (cx, cy),
            })

        # Prune disappeared tracks
        for tid in list(self.tracks.keys()):
            if tid not in active_ids:
                del self.tracks[tid]

        return results

    # ── Internal helpers ──────────────────────────────────────

    def _get_track(self, cx, cy, max_dist=80):
        """Match centroid to nearest existing track or create a new one."""
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

    def _classify(self, tid):
        """
        Multi-feature gait classification.
        Returns (label, score_percent).
        """
        trail = list(self.tracks[tid])
        if len(trail) < self.MIN_FRAMES:
            return "Detecting...", 0

        positions = np.array([(x, y)   for x, y, *_ in trail])
        areas     = np.array([a         for *_, a, _ in trail])
        heights   = np.array([h         for *_, h    in trail])

        # ── Feature 1: average speed (px/frame) ──
        diffs     = np.diff(positions, axis=0)
        distances = np.hypot(diffs[:, 0], diffs[:, 1])
        avg_speed = float(np.mean(distances))

        # ── Feature 2: vertical oscillation ──
        # Walking/running produce a rhythmic up-down bounce in the y-axis.
        y_diffs       = np.diff(positions[:, 1])
        y_oscillation = float(np.std(y_diffs))

        # ── Feature 3: silhouette area variation (coefficient of variation) ──
        # Running stretches/compresses the blob more than walking.
        area_mean = float(np.mean(areas)) + 1e-6
        area_cv   = float(np.std(areas)) / area_mean

        # ── Feature 4: bounding-box height variation ──
        height_mean = float(np.mean(heights)) + 1e-6
        height_cv   = float(np.std(heights)) / height_mean

        # ── Combined gait score (higher = more vigorous motion) ──
        motion_score = (
            avg_speed     * 1.0 +
            y_oscillation * 1.5 +
            area_cv       * 30  +
            height_cv     * 20
        )

        # ── Decision boundaries ──
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
