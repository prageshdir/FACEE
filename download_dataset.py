"""
Dataset Download Helper
Downloads and sets up LFW (Labeled Faces in the Wild) dataset for face recognition.

Run this script once before starting the main app:
    python download_dataset.py
"""

import os
import sys
import zipfile
import urllib.request
import shutil

LFW_URL = "http://vis-www.cs.umass.edu/lfw/lfw.tgz"
LFW_PAIRS_URL = "http://vis-www.cs.umass.edu/lfw/pairsDevTest.txt"

DATASET_DIR = "dataset"
KNOWN_FACES_DIR = os.path.join(DATASET_DIR, "known_faces")
LFW_SUBSET_NAMES = [
    "George_W_Bush",
    "Colin_Powell",
    "Tony_Blair",
    "Donald_Rumsfeld",
    "Gerhard_Schroeder",
]  # Persons with many images in LFW — good for quick demo


def download_lfw_via_kaggle():
    """Try downloading LFW via kaggle CLI."""
    print("Attempting Kaggle download of LFW dataset...")
    try:
        ret = os.system("kaggle datasets download -d jessicali9530/lfw-dataset -p dataset/ --unzip")
        if ret == 0:
            print("Kaggle download successful!")
            return True
    except Exception:
        pass
    return False


def create_sample_persons():
    """
    If LFW data is available in dataset/lfw, copy a few well-known persons
    to known_faces/ for a quick working demo.
    """
    lfw_root = os.path.join(DATASET_DIR, "lfw")
    if not os.path.exists(lfw_root):
        # Check alternate paths from Kaggle unzip
        for alt in ["dataset/lfw-deepfunneled", "dataset/lfw_funneled"]:
            if os.path.exists(alt):
                lfw_root = alt
                break
        else:
            print("[!] LFW folder not found. Skipping sample person setup.")
            return

    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    count = 0
    for person in LFW_SUBSET_NAMES:
        src_dir = os.path.join(lfw_root, person)
        if not os.path.exists(src_dir):
            continue
        dst_dir = os.path.join(KNOWN_FACES_DIR, person)
        os.makedirs(dst_dir, exist_ok=True)
        images = [f for f in os.listdir(src_dir) if f.lower().endswith((".jpg", ".png"))]
        # Copy up to 5 images per person
        for img in images[:5]:
            shutil.copy(os.path.join(src_dir, img), os.path.join(dst_dir, img))
            count += 1
        print(f"  Copied {min(len(images), 5)} images for {person}")

    print(f"\nTotal {count} images copied to {KNOWN_FACES_DIR}")
    print("Now run: python app.py   to start the application.")


def manual_guide():
    print("""
──────────────────────────────────────────────────────────
MANUAL DATASET SETUP (if automatic download fails)
──────────────────────────────────────────────────────────

Option 1 — LFW Dataset (Recommended for face recognition):
  1. Go to: https://www.kaggle.com/datasets/jessicali9530/lfw-dataset
  2. Download the dataset ZIP
  3. Extract and place the "lfw" folder inside:  dataset/lfw/

Option 2 — Custom webcam capture (No download needed!):
  1. Start the app:  python app.py
  2. Click "▶ Start Camera"
  3. Stand in front of the webcam
  4. Click "📸 Register New Face"
  5. Enter your name
  → Your face is now in the database!

Option 3 — Add photos manually:
  Place photos in this structure:
    dataset/
      known_faces/
        Your_Name/
          photo1.jpg
          photo2.jpg
  Then run the app — it auto-detects new faces on startup.

──────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    print("=" * 60)
    print("Face & Gait Recognition — Dataset Setup")
    print("=" * 60)

    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, "gait_data"), exist_ok=True)

    # Try Kaggle first
    success = download_lfw_via_kaggle()
    if success:
        create_sample_persons()
    else:
        manual_guide()

    # Delete cached encodings so they're rebuilt fresh
    enc_path = "models/face_encodings.pkl"
    if os.path.exists(enc_path):
        os.remove(enc_path)
        print("Cleared old face encodings cache.")

    print("\nSetup complete. Run:  python app.py")
