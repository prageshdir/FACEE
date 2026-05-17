"""
Gait Analyzer Module
Analyzes walking patterns from tracked person centroids over time.

Simple but effective approach:
  1. Track centroid positions per person across frames
  2. Measure stride frequency (oscillation in x/y)
  3. Classify gait as: Walking, Running, Standing, Unknown
  4. Compute a gait score (0-100)
"""

import numpy as np
from collections import deque
import time


class GaitAnalyzer:
    TRAIL_LENGTH = 40       # number of past frames to keep per track
    MIN_FRAMES = 15         # need at least this many frames to classify
    FPS_ESTIMATE = 25       # assumed camera FPS for time-based metrics

    def __init__(self):
        # track_id -> deque of (x, y, timestamp)
        self.tracks = {}
        self._next_id = 0

    # ------------------------------------------------------------------
    # Tracking helpers
    # ------------------------------------------------------------------

    def _match_track(self, centroid, max_dist=80):
        """Find the closest existing track for a centroid, or create new."""
        cx, cy = centroid
        best_id = None
        best_d = float("inf")
        for tid, trail in self.tracks.items():
            if not trail:
                continue
            lx, ly, _ = trail[-1]
            d = np.hypot(cx - lx, cy - ly)
            if d < best_d:
                best_d = d
                best_id = tid
        if best_id is not None and best_d < max_dist:
            return best_id
        # New track
        new_id = self._next_id
        self._next_id += 1
        self.tracks[new_id] = deque(maxlen=self.TRAIL_LENGTH)
        return new_id

    def update(self, persons):
        """
        Feed current frame's detected persons.
        Returns list of dicts per person: {track_id, gait_label, gait_score, speed}
        """
        active_ids = set()
        results = []

        for p in persons:
            cx, cy = p["centroid"]
            tid = self._match_track((cx, cy))
            self.tracks[tid].append((cx, cy, time.time()))
            active_ids.add(tid)

            label, score, speed = self._analyze_track(tid)
            results.append({
                "track_id": tid,
                "gait_label": label,
                "gait_score": score,
                "speed": speed,
                "centroid": (cx, cy),
                "bbox": p["bbox"],
            })

        # Prune stale tracks (not updated this frame)
        stale = [tid for tid in self.tracks if tid not in active_ids]
        for tid in stale:
            del self.tracks[tid]

        return results

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _analyze_track(self, track_id):
        """
        Analyze the centroid trail for a single track.
        Returns (label, score, speed_px_per_sec).
        """
        trail = list(self.tracks[track_id])
        if len(trail) < self.MIN_FRAMES:
            return "Detecting...", 0, 0.0

        positions = np.array([(x, y) for x, y, _ in trail])
        times = np.array([t for _, _, t in trail])

        # --- Speed (pixels per second) ---
        total_dist = np.sum(np.hypot(np.diff(positions[:, 0]), np.diff(positions[:, 1])))
        elapsed = times[-1] - times[0] + 1e-6
        speed = total_dist / elapsed  # px/sec

        # --- Lateral oscillation (stride signature) ---
        x_vals = positions[:, 0].astype(float)
        x_demeaned = x_vals - np.mean(x_vals)
        # Zero-crossings in x signal ~ stride rate
        sign_changes = np.diff(np.sign(x_demeaned))
        zero_crossings = int(np.sum(sign_changes != 0))
        stride_rate = zero_crossings / (elapsed + 1e-6)  # crossings per sec

        # --- Vertical oscillation ---
        y_vals = positions[:, 1].astype(float)
        y_std = float(np.std(y_vals))

        # --- Classification rules (simple threshold-based) ---
        if speed < 8:
            label = "Standing"
            score = max(0, int(100 - speed * 5))
        elif speed < 35:
            # Walking: moderate speed, regular stride
            rhythm_bonus = min(40, int(stride_rate * 15))
            score = min(100, 40 + rhythm_bonus + int(y_std * 0.5))
            label = "Walking"
        else:
            # Running: high speed
            score = min(100, 60 + int(stride_rate * 8))
            label = "Running"

        return label, int(np.clip(score, 0, 100)), round(speed, 1)

    def draw_gait_info(self, frame, gait_results):
        """Overlay gait labels on frame."""
        import cv2
        for g in gait_results:
            x, y, w, h = g["bbox"]
            label = f"{g['gait_label']} ({g['gait_score']}%)"
            cv2.putText(
                frame, label,
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2,
            )
        return frame
