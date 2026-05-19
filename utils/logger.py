"""
Logger
Saves each recognition event to logs/recognition_log.csv
"""

import os
import csv
import datetime

LOG_FILE = "logs/recognition_log.csv"


class RecognitionLogger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)
        # Create CSV with headers if it doesn't exist
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="") as f:
                csv.writer(f).writerow(["Time", "Name", "Confidence%", "Gait"])
        self.recent = []  # keep last 30 entries in memory for GUI

    def log(self, name, confidence, gait="N/A"):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {"time": now, "name": name, "confidence": confidence, "gait": gait}

        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow([now, name, confidence, gait])

        self.recent.append(row)
        if len(self.recent) > 30:
            self.recent.pop(0)
