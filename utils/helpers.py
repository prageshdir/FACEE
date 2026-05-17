"""
Utility helpers for drawing and frame manipulation.
"""

import cv2
import datetime
import numpy as np


def timestamp_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def resize_frame(frame, width=640):
    """Resize frame maintaining aspect ratio."""
    h, w = frame.shape[:2]
    ratio = width / w
    new_h = int(h * ratio)
    return cv2.resize(frame, (width, new_h))


def draw_label(frame, text, position, font_scale=0.6, color=(0, 255, 0),
               bg_color=(0, 0, 0), thickness=1):
    """Draw text with a filled background rectangle for readability."""
    x, y = position
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness + 1)
    # Background
    cv2.rectangle(frame, (x, y - th - 4), (x + tw + 2, y + baseline), bg_color, -1)
    # Text
    cv2.putText(frame, text, (x + 1, y), font, font_scale, color, thickness + 1)
    return frame


def draw_timestamp(frame):
    """Overlay current timestamp at the bottom-left of the frame."""
    ts = timestamp_str()
    h, w = frame.shape[:2]
    draw_label(frame, ts, (10, h - 10), font_scale=0.45, color=(200, 200, 200))
    return frame


def draw_face_result(frame, result):
    """
    Draw face recognition result on frame.
    result dict: {name, confidence, location}
    location = (top, right, bottom, left)
    """
    top, right, bottom, left = result["location"]
    name = result["name"]
    conf = result["confidence"]

    color = (0, 200, 0) if name != "Unknown" else (0, 0, 220)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    label = f"{name}  {conf:.1f}%"
    draw_label(frame, label, (left, top - 5), color=color)
    return frame


def save_screenshot(frame, prefix="screenshot"):
    """Save frame to screenshots/ folder."""
    import os
    os.makedirs("screenshots", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"screenshots/{prefix}_{ts}.jpg"
    cv2.imwrite(path, frame)
    return path
