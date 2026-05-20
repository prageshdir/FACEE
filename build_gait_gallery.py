"""
Build Gait Gallery from CASIA-B Dataset
========================================
Run this ONCE to process the dataset and train the GEI + PCA + LDA + KNN model.
The model is saved to  models/gait_model.pkl  and auto-loaded by the app.

Key accuracy decisions baked in:
  - nm-01 + nm-02 used as gallery (2 templates per person instead of 1).
  - bg-01 (bag condition) used as probe — harder than nm-02 and more realistic.
  - GEI vectors are L2-normalised before PCA so scale differences don't dominate.
  - LDA after PCA specifically maximises between-subject separability.
  - KNN k=3 with distance weighting for robustness at decision boundaries.

Usage
-----
    python build_gait_gallery.py --data /path/to/casia-b/output

    # More subjects → higher accuracy
    python build_gait_gallery.py --data /path/to/output --subjects 50

    # Use all normal sequences as gallery
    python build_gait_gallery.py --data /path/to/output \\
        --gallery nm-01 nm-02 nm-03 nm-04 --probe bg-01 bg-02 cl-01 cl-02

Expected folder structure (CASIA-B)
-------------------------------------
    output/
        001/
            nm-01/090/*.png
            nm-02/090/*.png
            bg-01/090/*.png
        002/ ...
"""

import argparse
import os
import sys

import cv2
import numpy as np
from sklearn.metrics import accuracy_score

sys.path.insert(0, os.path.dirname(__file__))
from gait_module.gait_recognizer import GaitRecognizer, GEI_H, GEI_W


# ── Data loading ──────────────────────────────────────────────────────────────

def load_silhouettes(root: str, subject_id: str,
                     seq_id: str, view: str) -> list:
    """Load all PNG frames for one subject/sequence/view as float32 [0,1]."""
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


def build_dataset(root: str, max_subjects: int, view: str,
                  gallery_seqs: list[str], probe_seqs: list[str]):
    """
    Walk the CASIA-B directory tree and compute GEIs.
    Gallery: merge all gallery_seqs for each subject → one GEI per subject.
    Probe:   one separate GEI per probe sequence per subject.
    Returns (X_gallery, y_gallery, X_probe, y_probe).
    """
    X_gallery, y_gallery = [], []
    X_probe,   y_probe   = [], []
    valid = 0

    for subject_id in sorted(os.listdir(root)):
        if valid >= max_subjects:
            break
        subject_path = os.path.join(root, subject_id)
        if not os.path.isdir(subject_path) or subject_id.startswith("."):
            continue

        # Skip subject if any required sequence is missing
        missing = [s for s in gallery_seqs + probe_seqs
                   if not os.path.isdir(os.path.join(subject_path, s, view))]
        if missing:
            continue

        # Gallery: pool all gallery sequences into one averaged GEI
        gallery_frames = []
        for seq in gallery_seqs:
            gallery_frames += load_silhouettes(root, subject_id, seq, view)
        if not gallery_frames:
            continue
        gei = GaitRecognizer.compute_gei(gallery_frames)
        X_gallery.append(gei.flatten())
        y_gallery.append(subject_id)

        # Probe: one GEI per sequence
        for seq in probe_seqs:
            frames = load_silhouettes(root, subject_id, seq, view)
            if not frames:
                continue
            gei = GaitRecognizer.compute_gei(frames)
            X_probe.append(gei.flatten())
            y_probe.append(subject_id)

        valid += 1
        print(f"  Loaded {subject_id}: gallery {len(gallery_frames)} frames, "
              f"{len(probe_seqs)} probe seq(s)")

    print(f"\n  Subjects loaded : {valid}")
    print(f"  Gallery GEIs   : {len(X_gallery)}")
    print(f"  Probe   GEIs   : {len(X_probe)}")
    return (np.array(X_gallery, dtype=np.float32),
            np.array(y_gallery),
            np.array(X_probe, dtype=np.float32),
            np.array(y_probe))


# ── Evaluation ───────────────────────────────────────────────────────────────

def evaluate(recognizer: GaitRecognizer,
             X_probe: np.ndarray, y_probe: np.ndarray):
    """Rank-1 identification report on the probe set."""
    from sklearn.preprocessing import normalize

    X_norm = normalize(X_probe, norm="l2")
    X_pca  = recognizer.pca.transform(X_norm)
    X_feat = recognizer.lda.transform(X_pca) if recognizer.lda is not None else X_pca
    dists, indices = recognizer.knn.kneighbors(X_feat)

    rev          = {v: k for k, v in recognizer.label_map.items()}
    y_true_names = [str(y) for y in y_probe]
    y_pred_int   = recognizer.knn.predict(X_feat)
    y_pred_names = [recognizer.label_map.get(int(p), "?") for p in y_pred_int]

    acc = accuracy_score(y_true_names, y_pred_names)

    print("\n" + "=" * 60)
    print(f"  Rank-1 Identification Accuracy : {acc * 100:.1f}%")
    print(f"  Probe samples tested           : {len(y_probe)}")
    print("=" * 60)

    correct   = sum(a == p for a, p in zip(y_true_names, y_pred_names))
    incorrect = len(y_probe) - correct
    print(f"  Correct   : {correct}")
    print(f"  Incorrect : {incorrect}")

    print("\nPer-probe results:")
    hdr = f"  {'#':>3}  {'Actual':>8}  {'Predicted':>8}  {'Dist':>7}  Result"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for i, (actual, pred, dist) in enumerate(
            zip(y_true_names, y_pred_names, dists.flatten())):
        mark = "✓" if actual == pred else "✗"
        print(f"  {i+1:>3}  {actual:>8}  {pred:>8}  {dist:>7.3f}  {mark}")

    return acc


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Build CASIA-B gait gallery — GEI + PCA + LDA + KNN")
    ap.add_argument("--data",     required=True,
                    help="Path to CASIA-B output/ directory")
    ap.add_argument("--subjects", type=int, default=20,
                    help="Max subjects to use (default: 20, more = better)")
    ap.add_argument("--view",     default="090",
                    help="View-angle folder (default: 090)")
    ap.add_argument("--gallery",  nargs="+", default=["nm-01", "nm-02"],
                    help="Gallery sequences (default: nm-01 nm-02)")
    ap.add_argument("--probe",    nargs="+", default=["bg-01"],
                    help="Probe sequences  (default: bg-01)")
    ap.add_argument("--pca",      type=int, default=None,
                    help="PCA components before LDA (default: auto ≥95%% var)")
    args = ap.parse_args()

    if not os.path.isdir(args.data):
        print(f"[ERROR] Directory not found: {args.data}")
        sys.exit(1)

    overlap = set(args.gallery) & set(args.probe)
    if overlap:
        print(f"[ERROR] Sequences in both gallery and probe: {overlap}")
        sys.exit(1)

    print(f"Dataset      : {args.data}")
    print(f"Subjects     : up to {args.subjects}")
    print(f"View angle   : {args.view}")
    print(f"Gallery seqs : {args.gallery}")
    print(f"Probe seqs   : {args.probe}")
    print()

    print("Step 1 — Loading silhouettes and computing GEIs …")
    X_gal, y_gal, X_prob, y_prob = build_dataset(
        args.data, args.subjects, args.view, args.gallery, args.probe)

    if len(X_gal) == 0:
        print("[ERROR] No gallery GEIs found. Check --data path and names.")
        sys.exit(1)

    print("\nStep 2 — Training PCA + LDA + KNN …")
    rec = GaitRecognizer()
    rec.train(X_gal, y_gal, pca_components=args.pca)

    if len(X_prob) > 0:
        print("\nStep 3 — Evaluating on probe set …")
        evaluate(rec, X_prob, y_prob)
    else:
        print("\nNo probe sequences found — skipping evaluation.")

    print(f"\nModel saved to  models/gait_model.pkl")
    print("Run  python app.py  — the gait recognizer loads automatically.")


if __name__ == "__main__":
    main()
