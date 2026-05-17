"""
Gait Analyzer
Tracks a person's position over time and classifies their movement.

Logic:
  - Keep last 30 positions (centroid trail)
  - Measure how fast the centroid moves (speed in pixels/frame)
  - Classify: Standing | Walking | Running
"""

from collections import deque
import numpy as np
import time


class GaitAnalyzer:
    TRAIL_LEN = 30      # how many past positions to remember
    MIN_FRAMES = 10     # need this many frames before classifying

    def __init__(self):
        # Each track: track_id -> deque of (cx, cy, time)
        self.tracks = {}
        self._next_id = 0

    def update(self, persons):
        """
        Feed current frame's detected persons.
        Returns list of results: {track_id, label, score, bbox, centroid}
        """
        active_ids = set()
        results = []

        for p in persons:
            cx, cy = p["centroid"]
            tid = self._get_track(cx, cy)
            self.tracks[tid].append((cx, cy, time.time()))
            active_ids.add(tid)

            label, score = self._classify(tid)
            results.append({
                "track_id": tid,
                "label": label,
                "score": score,
                "bbox": p["bbox"],
                "centroid": (cx, cy)
            })

        # Remove tracks that disappeared
        for tid in list(self.tracks.keys()):
            if tid not in active_ids:
                del self.tracks[tid]

        return results

    def _get_track(self, cx, cy, max_dist=80):
        """Match centroid to nearest existing track, or create new track."""
        best_id = None
        best_dist = float("inf")

        for tid, trail in self.tracks.items():
            if not trail:
                continue
            lx, ly, _ = trail[-1]
            d = np.hypot(cx - lx, cy - ly)
            if d < best_dist:
                best_dist = d
                best_id = tid

        if best_id is not None and best_dist < max_dist:
            return best_id

        # New person detected
        new_id = self._next_id
        self._next_id += 1
        self.tracks[new_id] = deque(maxlen=self.TRAIL_LEN)
        return new_id

    def _classify(self, tid):
        """
        Classify gait from centroid trail.
        Returns (label, score_percent).
        """
        trail = list(self.tracks[tid])
        if len(trail) < self.MIN_FRAMES:
            return "Detecting...", 0

        positions = np.array([(x, y) for x, y, _ in trail])

        # Calculate frame-to-frame movement distances
        diffs = np.diff(positions, axis=0)
        distances = np.hypot(diffs[:, 0], diffs[:, 1])
        avg_speed = float(np.mean(distances))  # pixels per frame

        # Classify based on speed
        if avg_speed < 3:
            label = "Standing"
            score = 90
        elif avg_speed < 15:
            label = "Walking"
            score = min(100, int(avg_speed * 6))
        else:
            label = "Running"
            score = min(100, int(avg_speed * 3))

        return label, score
