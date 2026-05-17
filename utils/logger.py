"""
Recognition Logger
Writes recognition events to a CSV log file and keeps an in-memory list
for display in the GUI.
"""

import os
import csv
import datetime


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "recognition_log.csv")


class RecognitionLogger:
    MAX_MEMORY = 200  # entries to keep in RAM

    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self._memory = []  # recent entries for GUI
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Name", "Confidence", "Gait", "GaitScore"])

    def log(self, name, confidence, gait_label="N/A", gait_score=0):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {
            "timestamp": ts,
            "name": name,
            "confidence": confidence,
            "gait": gait_label,
            "gait_score": gait_score,
        }
        # Append to CSV
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ts, name, confidence, gait_label, gait_score])

        # Keep in memory (drop oldest if over limit)
        self._memory.append(row)
        if len(self._memory) > self.MAX_MEMORY:
            self._memory.pop(0)

    def recent(self, n=20):
        """Return the n most recent log entries."""
        return list(reversed(self._memory[-n:]))

    def clear_memory(self):
        self._memory.clear()
