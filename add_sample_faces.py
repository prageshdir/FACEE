"""
Quick Sample Face Creator
Generates placeholder face images using webcam snapshots for demo purposes.
Run this to add yourself and test faces to the database without Kaggle.

Usage:
    python add_sample_faces.py
"""

import os
import cv2
import sys

KNOWN_FACES_DIR = "dataset/known_faces"


def capture_faces(name, count=5):
    """Capture `count` images of a person via webcam."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(person_dir, exist_ok=True)

    print(f"\nCapturing {count} images for '{name}'.")
    print("Press SPACE to capture, ESC to quit early.\n")

    captured = 0
    while captured < count:
        ret, frame = cap.read()
        if not ret:
            continue
        display = frame.copy()
        cv2.putText(display,
                    f"Press SPACE to capture ({captured}/{count}) — ESC to quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow(f"Register: {name}", display)
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            path = os.path.join(person_dir, f"{name}_{captured + 1:03d}.jpg")
            cv2.imwrite(path, frame)
            print(f"  Saved: {path}")
            captured += 1
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {captured} images for '{name}'.\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Sample Face Registration Tool")
    print("=" * 50)

    while True:
        name = input("\nEnter person name (or 'done' to finish): ").strip()
        if name.lower() == "done" or not name:
            break
        name = name.replace(" ", "_")
        n = input("How many photos to capture? [5]: ").strip()
        count = int(n) if n.isdigit() else 5
        capture_faces(name, count)

    # Remove cached encodings so they rebuild
    enc = "models/face_encodings.pkl"
    if os.path.exists(enc):
        os.remove(enc)
        print("Face encoding cache cleared — will rebuild on next launch.")

    print("\nDone! Run: python app.py")
