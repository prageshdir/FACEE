"""
Drawing helpers for overlaying text/boxes on OpenCV frames.
"""

import cv2
import datetime
import os


def draw_box(frame, x, y, w, h, color, label):
    """Draw a colored rectangle with a label above it."""
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    # Background rectangle for text so it's readable on any background
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    cv2.rectangle(frame, (x, y - th - 8), (x + tw + 4, y), color, -1)
    cv2.putText(frame, label, (x + 2, y - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


def draw_timestamp(frame):
    """Put current time at the bottom-left corner."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    h = frame.shape[0]
    cv2.putText(frame, ts, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)


def save_screenshot(frame):
    """Save current frame to screenshots/ folder."""
    os.makedirs("screenshots", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"screenshots/capture_{ts}.jpg"
    cv2.imwrite(path, frame)
    return path
