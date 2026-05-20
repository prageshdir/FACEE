"""
Build Gait Gallery from CASIA-B Dataset
========================================
Run this ONCE to process the dataset and train the GEI + PCA + KNN model.
The model is saved to  models/gait_model.pkl  and auto-loaded by the app.

Usage
-----
    python build_gait_gallery.py --data /path/to/casia-b/output

    # Specify number of subjects and the view angle to use
    python build_gait_gallery.py --data /kaggle/input/casia-b/output --subjects 20 --view 090

    # Combine nm-01 AND nm-02 as gallery (more training data → higher accuracy)
    python build_gait_gallery.py --data /path/to/output --gallery nm-01 nm-02

Expected folder structure
-------------------------
    output/
        001/
            nm-01/
                090/
                    001-nm-01-090-001.png
                    001-nm-01-090-002.png
                    ...
            nm-02/090/*.png
            bg-01/090/*.png
        002/
            ...

This matches exactly the CASIA-B structure used in the notebook.
"""

import argparse
import os
import sys

import cv2
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix

# Allow running from the repo root
sys.path.insert(0, os.path.dirname(__file__))
from gait_module.gait_recognizer import GaitRecognizer, GEI_H, GEI_W


# ── Data loading ──────────────────────────────────────────────────────────────

def load_silhouettes(root: str, subject_id: str, seq_id: str, view: str) -> list:
    """Load all PNG frames for one subject/sequence/view as float32 arrays."""
    path = os.path.join(root, subject_id, seq_id, view)
    if not os.path.isdir(path):
        return []
    silhouettes = []
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".png"):
            continue
        img = cv2.imread(os.path.join(path, fname), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        img = cv2.resize(img, (GEI_W, GEI_H), interpolation=cv2.INTER_LINEAR)
        silhouettes.append(img.astype(np.float32) / 255.0)
    return silhouettes


def build_dataset(root: str, subjects: int, view: str,
                  gallery_seqs: list[str], probe_seqs: list[str]):
    """
    Walk the CASIA-B directory and compute GEIs for gallery and probe sets.
    Returns (X_gallery, y_gallery, X_probe, y_probe).
    """
    X_gallery, y_gallery = [], []
    X_probe,   y_probe   = [], []

    valid_subjects = 0
    for subject_id in sorted(os.listdir(root)):
        if valid_subjects >= subjects:
            break
        subject_path = os.path.join(root, subject_id)
        if not os.path.isdir(subject_path) or subject_id.startswith("."):
            continue

        # Verify all required sequences exist
        all_seqs = gallery_seqs + probe_seqs
        missing = [s for s in all_seqs
                   if not os.path.isdir(os.path.join(subject_path, s, view))]
        if missing:
            continue

        # ── Gallery: merge all gallery sequences into one GEI ──
        gallery_frames = []
        for seq in gallery_seqs:
            gallery_frames += load_silhouettes(root, subject_id, seq, view)
        if not gallery_frames:
            continue
        gei = GaitRecognizer.compute_gei(gallery_frames)
        X_gallery.append(gei.flatten())
        y_gallery.append(subject_id)

        # ── Probe: one GEI per probe sequence ──
        for seq in probe_seqs:
            frames = load_silhouettes(root, subject_id, seq, view)
            if not frames:
                continue
            gei = GaitRecognizer.compute_gei(frames)
            X_probe.append(gei.flatten())
            y_probe.append(subject_id)

        valid_subjects += 1
        print(f"  Loaded subject {subject_id} "
              f"(gallery: {len(gallery_frames)} frames, "
              f"{len(probe_seqs)} probe sequences)")

    print(f"\nTotal subjects: {valid_subjects}")
    print(f"Gallery GEIs : {len(X_gallery)}")
    print(f"Probe   GEIs : {len(X_probe)}")
    return (np.array(X_gallery), np.array(y_gallery),
            np.array(X_probe),   np.array(y_probe))


# ── Evaluation ───────────────────────────────────────────────────────────────

def evaluate(recognizer: GaitRecognizer, X_probe: np.ndarray, y_probe: np.ndarray):
    """Run rank-1 identification on the probe set and print a report."""
    X_pca = recognizer.pca.transform(X_probe)
    distances, indices = recognizer.knn.kneighbors(X_pca)

    rev = {v: k for k, v in recognizer.label_map.items()}
    y_true_int = np.array([rev.get(str(y), -1) for y in y_probe])
    y_pred_int = recognizer.knn.predict(X_pca)

    y_true_names = [str(y) for y in y_probe]
    y_pred_names = [recognizer.label_map.get(int(p), "?") for p in y_pred_int]

    acc = accuracy_score(y_true_names, y_pred_names)

    print("\n" + "=" * 55)
    print(f"  Rank-1 Identification Accuracy : {acc * 100:.1f}%")
    print(f"  Probe samples tested           : {len(y_probe)}")
    print("=" * 55)

    print("\nIndividual results:")
    header = f"{'#':>3}  {'Actual':>8}  {'Predicted':>8}  {'Dist':>7}  Result"
    print(header)
    print("-" * len(header))
    for i, (actual, pred, dist) in enumerate(
            zip(y_true_names, y_pred_names, distances.flatten())):
        ok = "✓" if actual == pred else "✗"
        print(f"{i+1:>3}  {actual:>8}  {pred:>8}  {dist:>7.3f}  {ok}")

    return acc


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build CASIA-B gait gallery and train GEI+PCA+KNN model")
    parser.add_argument("--data",     required=True,
                        help="Path to the CASIA-B output/ directory")
    parser.add_argument("--subjects", type=int, default=20,
                        help="Max number of subjects to load (default: 20)")
    parser.add_argument("--view",     default="090",
                        help="View angle folder name (default: 090)")
    parser.add_argument("--gallery",  nargs="+", default=["nm-01", "nm-02"],
                        help="Sequences to use as gallery/training "
                             "(default: nm-01 nm-02)")
    parser.add_argument("--probe",    nargs="+", default=["bg-01"],
                        help="Sequences to use as probe/test "
                             "(default: bg-01)")
    parser.add_argument("--pca",      type=int, default=None,
                        help="Number of PCA components (default: auto)")
    args = parser.parse_args()

    if not os.path.isdir(args.data):
        print(f"[ERROR] Dataset directory not found: {args.data}")
        sys.exit(1)

    print(f"Dataset     : {args.data}")
    print(f"Subjects    : up to {args.subjects}")
    print(f"View angle  : {args.view}")
    print(f"Gallery seqs: {args.gallery}")
    print(f"Probe seqs  : {args.probe}")
    print()

    # Validate no overlap between gallery and probe
    overlap = set(args.gallery) & set(args.probe)
    if overlap:
        print(f"[ERROR] Sequences appear in both gallery and probe: {overlap}")
        sys.exit(1)

    print("Step 1 — Loading silhouettes and computing GEIs …")
    X_gal, y_gal, X_prob, y_prob = build_dataset(
        args.data, args.subjects, args.view, args.gallery, args.probe)

    if len(X_gal) == 0:
        print("[ERROR] No gallery GEIs found. Check --data path and sequence names.")
        sys.exit(1)

    print("\nStep 2 — Training PCA + KNN …")
    recognizer = GaitRecognizer()
    recognizer.train(X_gal, y_gal, n_components=args.pca)

    if len(X_prob) > 0:
        print("\nStep 3 — Evaluating on probe set …")
        evaluate(recognizer, X_prob, y_prob)
    else:
        print("\nNo probe sequences found — skipping evaluation.")

    print(f"\nModel saved to  models/gait_model.pkl")
    print("Run  python app.py  — the gait recognizer will load automatically.")


if __name__ == "__main__":
    main()
