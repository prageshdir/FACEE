"""
Accuracy measurement for the FACEE Face Recognition system.

Two test modes run automatically:
  1. Leave-One-Out Cross-Validation (LOOCV) — for persons with ≥2 registered images.
  2. Augmentation Test              — for persons with only 1 image; tests
     brightness/contrast/flip variants to simulate real-world variation.

Usage:
    python measure_accuracy.py
"""

import os
import sys
import cv2
import numpy as np
import pickle
from itertools import combinations

KNOWN_FACES_DIR = "dataset/known_faces"
CONFIDENCE_THRESHOLD = 80   # must match face_recognizer.py
FACE_SIZE = (100, 100)

# ── Augmentation helpers ──────────────────────────────────────

def augment(img):
    """Return a list of augmented variants of a grayscale face image."""
    variants = []
    # Brightness darker / brighter
    for alpha, beta in [(0.7, -20), (1.3, 20), (0.85, 10)]:
        v = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        variants.append(v)
    # Horizontal flip
    variants.append(cv2.flip(img, 1))
    # Small rotation ±10°
    h, w = img.shape
    for angle in (-10, 10):
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        variants.append(cv2.warpAffine(img, M, (w, h)))
    # Gaussian blur (simulate soft focus)
    variants.append(cv2.GaussianBlur(img, (5, 5), 0))
    return variants


# ── Dataset loader ────────────────────────────────────────────

def load_dataset():
    """
    Returns:
        persons  : dict  { name: [grayscale 100x100 np.array, ...] }
    """
    persons = {}
    if not os.path.isdir(KNOWN_FACES_DIR):
        return persons

    for name in sorted(os.listdir(KNOWN_FACES_DIR)):
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if not os.path.isdir(person_dir):
            continue
        imgs = []
        for fname in sorted(os.listdir(person_dir)):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            path = os.path.join(person_dir, fname)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                imgs.append(cv2.resize(img, FACE_SIZE))
        if imgs:
            persons[name] = imgs

    return persons


# ── LBPH train / predict helpers ─────────────────────────────

def train_model(images, labels):
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(images, np.array(labels))
    return model


def predict(model, img, label_map):
    label_id, distance = model.predict(img)
    confidence = max(0, int(100 - distance))
    if distance > CONFIDENCE_THRESHOLD:
        return "Unknown", confidence
    return label_map.get(label_id, "Unknown"), confidence


# ── Test 1: Leave-One-Out Cross-Validation ────────────────────

def run_loocv(persons):
    """
    For each person with ≥2 images: leave one image out, train on the rest,
    predict the held-out image.  Repeat for every image of every such person.
    """
    eligible = {n: imgs for n, imgs in persons.items() if len(imgs) >= 2}
    if not eligible:
        return None

    print("\n" + "=" * 60)
    print("TEST 1 — Leave-One-Out Cross-Validation (LOOCV)")
    print("=" * 60)

    all_correct = 0
    all_total   = 0
    results = {}

    for test_name, test_imgs in eligible.items():
        person_correct = 0
        person_total   = len(test_imgs)
        confidences    = []

        for held_out_idx in range(len(test_imgs)):
            # Build training set: all images of all persons, minus held-out
            train_images = []
            train_labels = []
            label_map    = {}
            reverse_map  = {}

            label_id = 0
            for name, imgs in persons.items():
                label_map[label_id]  = name
                reverse_map[name]    = label_id
                for i, img in enumerate(imgs):
                    if name == test_name and i == held_out_idx:
                        continue   # hold this one out
                    train_images.append(img)
                    train_labels.append(label_id)
                label_id += 1

            if len(set(train_labels)) < 1:
                continue

            model = train_model(train_images, train_labels)
            pred_name, conf = predict(model, test_imgs[held_out_idx], label_map)
            confidences.append(conf)

            correct = (pred_name == test_name)
            person_correct += int(correct)

            status = "✓" if correct else f"✗ (predicted: {pred_name})"
            print(f"  {test_name:15s}  img #{held_out_idx+1}  conf={conf:3d}%  {status}")

        results[test_name] = {
            "correct":  person_correct,
            "total":    person_total,
            "accuracy": person_correct / person_total * 100,
            "avg_conf": int(np.mean(confidences)) if confidences else 0,
        }
        all_correct += person_correct
        all_total   += person_total

    # Summary
    overall = all_correct / all_total * 100 if all_total else 0
    print()
    print(f"{'Person':<20} {'Correct':>7} {'Total':>6} {'Accuracy':>9} {'Avg Conf':>9}")
    print("-" * 55)
    for name, r in results.items():
        print(f"{name:<20} {r['correct']:>7} {r['total']:>6} {r['accuracy']:>8.1f}%  {r['avg_conf']:>7}%")
    print("-" * 55)
    print(f"{'OVERALL':<20} {all_correct:>7} {all_total:>6} {overall:>8.1f}%")

    return overall, results


# ── Test 2: Augmentation Test ─────────────────────────────────

def run_augmentation_test(persons):
    """
    For ALL persons: train on real images, test on augmented variants.
    Measures robustness to brightness, flip, rotation, blur.
    """
    if not persons:
        return None

    print("\n" + "=" * 60)
    print("TEST 2 — Augmentation Robustness Test")
    print("(trains on real images, tests on synthetic variants)")
    print("=" * 60)

    # Build full training set
    train_images = []
    train_labels = []
    label_map    = {}
    reverse_map  = {}

    for label_id, (name, imgs) in enumerate(persons.items()):
        label_map[label_id]  = name
        reverse_map[name]    = label_id
        for img in imgs:
            train_images.append(img)
            train_labels.append(label_id)

    model = train_model(train_images, train_labels)

    aug_labels = ["Darker", "Brighter", "Slight bright", "H-Flip", "Rot -10°", "Rot +10°", "Blur"]

    all_correct = 0
    all_total   = 0
    results     = {}

    for name, imgs in persons.items():
        person_correct = 0
        person_total   = 0

        for img in imgs:
            variants = augment(img)
            for aug_img in variants:
                pred_name, conf = predict(model, aug_img, label_map)
                correct = (pred_name == name)
                person_correct += int(correct)
                person_total   += 1

        pct = person_correct / person_total * 100 if person_total else 0
        results[name] = {"correct": person_correct, "total": person_total, "accuracy": pct}
        all_correct += person_correct
        all_total   += person_total
        print(f"  {name:15s}  {person_correct}/{person_total} variants correct  ({pct:.1f}%)")

    overall = all_correct / all_total * 100 if all_total else 0
    print()
    print(f"  Overall augmentation accuracy: {all_correct}/{all_total}  ({overall:.1f}%)")
    return overall, results


# ── Test 3: Rejection (Unknown) Test ─────────────────────────

def run_rejection_test(persons):
    """
    For each person: artificially create an 'unknown' face by heavily
    corrupting the image, then verify the model correctly labels it Unknown.
    """
    if not persons:
        return None

    print("\n" + "=" * 60)
    print("TEST 3 — Unknown/Rejection Rate")
    print("(heavy noise added → should be rejected as Unknown)")
    print("=" * 60)

    train_images = []
    train_labels = []
    label_map    = {}

    for label_id, (name, imgs) in enumerate(persons.items()):
        label_map[label_id] = name
        for img in imgs:
            train_images.append(img)
            train_labels.append(label_id)

    model = train_model(train_images, train_labels)

    correct_reject = 0
    total_tests    = 0

    for name, imgs in persons.items():
        for img in imgs:
            # Heavy noise: random pixel block
            noise_img = np.random.randint(0, 256, FACE_SIZE, dtype=np.uint8)
            pred_name, _ = predict(model, noise_img, label_map)
            correct_reject += int(pred_name == "Unknown")
            total_tests    += 1

    pct = correct_reject / total_tests * 100 if total_tests else 0
    print(f"  Correctly rejected {correct_reject}/{total_tests} noise images as Unknown  ({pct:.1f}%)")
    return pct


# ── Main ──────────────────────────────────────────────────────

def main():
    try:
        import cv2
        if not hasattr(cv2, "face"):
            print("[ERROR] opencv-contrib-python required.")
            print("  pip install opencv-contrib-python==4.10.0.84")
            sys.exit(1)
    except ImportError:
        print("[ERROR] OpenCV not installed.")
        sys.exit(1)

    persons = load_dataset()

    if not persons:
        print("\n[!] No faces found in dataset/known_faces/")
        print("    Register at least one person via the app first, then re-run this script.")
        sys.exit(0)

    print(f"\nDataset: {len(persons)} person(s) found")
    for name, imgs in persons.items():
        print(f"  • {name}: {len(imgs)} image(s)")

    # Run tests
    loocv_result = run_loocv(persons)
    aug_result   = run_augmentation_test(persons)
    rej_result   = run_rejection_test(persons)

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if loocv_result:
        print(f"  LOOCV Accuracy (real-image holdout) : {loocv_result[0]:.1f}%")
    else:
        print("  LOOCV Accuracy                       : N/A (need ≥2 images per person)")

    if aug_result:
        print(f"  Augmentation Robustness              : {aug_result[0]:.1f}%")

    if rej_result is not None:
        print(f"  Unknown Rejection Rate               : {rej_result:.1f}%")

    print()
    if loocv_result and loocv_result[0] < 70:
        print("  Tip: Register more photos per person (different angles, lighting)")
        print("       to improve LOOCV accuracy.")
    print("=" * 60)


if __name__ == "__main__":
    main()
