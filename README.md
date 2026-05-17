# Deep Learning Based Face and Gait Recognition Using Surveillance Camera

**MCA Major Project**

---

## Overview

A real-time surveillance system that:
- Detects and recognizes faces from a webcam/CCTV feed
- Analyzes human walking patterns (gait) using motion tracking
- Displays person identity, confidence score, and gait status live
- Logs all recognition events with timestamps

---

## Project Structure

```
FACEE/
│
├── app.py                  ← Main application (run this)
├── download_dataset.py     ← Download LFW dataset via Kaggle
├── add_sample_faces.py     ← Register faces via webcam
├── requirements.txt
│
├── face_module/
│   ├── face_detector.py    ← Haar Cascade face detection
│   └── face_recognizer.py  ← face_recognition encoding & matching
│
├── gait_module/
│   ├── motion_detector.py  ← MOG2 background subtraction
│   └── gait_analyzer.py    ← Centroid tracking + pattern analysis
│
├── utils/
│   ├── logger.py           ← CSV event logger
│   └── helpers.py          ← Drawing utilities
│
├── dataset/
│   ├── known_faces/        ← Person photos (auto-loaded on start)
│   └── gait_data/          ← Gait dataset (optional)
│
├── models/                 ← Saved face encodings (auto-generated)
├── logs/                   ← recognition_log.csv
└── screenshots/            ← Saved frames
```

---

## Installation

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `dlib` (required by `face_recognition`) may need build tools.
> - **Windows:** Install Visual Studio Build Tools first.
> - **Ubuntu/Debian:** `sudo apt install build-essential cmake`
> - **macOS:** `xcode-select --install`

### 3. Add known faces

**Option A — Webcam capture (easiest)**
```bash
python add_sample_faces.py
```
Follow the on-screen prompts to capture photos of each person.

**Option B — Use LFW dataset (Kaggle)**
```bash
# Set up Kaggle credentials first: https://www.kaggle.com/docs/api
python download_dataset.py
```

**Option C — Manual**
```
dataset/
  known_faces/
    John_Doe/
      photo1.jpg
      photo2.jpg
    Jane_Smith/
      photo1.jpg
```

### 4. Run the application

```bash
python app.py
```

---

## How It Works

### Face Recognition

| Step | Method |
|------|--------|
| Detection | OpenCV Haar Cascade (`haarcascade_frontalface_default.xml`) |
| Encoding | 128-dimensional face embeddings via `face_recognition` (dlib FaceNet) |
| Matching | Euclidean distance with configurable tolerance (default 0.55) |
| Database | Pickle file (`models/face_encodings.pkl`) — auto-rebuilt when new images added |

### Gait Detection

| Step | Method |
|------|--------|
| Foreground extraction | MOG2 background subtractor |
| Person detection | Contour analysis + aspect ratio filter |
| Tracking | Centroid-based nearest-neighbor matching |
| Pattern analysis | Lateral oscillation + speed measurement |
| Classification | Standing / Walking / Running |

---

## GUI Features

| Button | Action |
|--------|--------|
| ▶ Start Camera | Opens webcam and starts detection |
| ■ Stop Camera | Stops video feed |
| 📸 Register New Face | Capture current frame and save as new person |
| 💾 Save Screenshot | Save annotated frame to screenshots/ |
| 🔄 Reload Face DB | Reload faces from disk without restarting |
| 🗑️ Clear Log | Clear recognition log panel |

---

## Output Display

Each frame shows:
- **Green box** — recognized person with name + confidence %
- **Red box** — unknown person
- **Orange box** — detected moving person (gait tracking)
- **Cyan text** — gait classification + score
- **FPS counter** — top-left
- **Timestamp** — bottom-left

---

## Configuration

Edit constants at the top of `app.py`:

```python
CAMERA_INDEX = 0       # 0=built-in webcam, 1=external camera
LOG_INTERVAL = 3       # seconds between duplicate log entries
RECOGNITION_SCALE = 0  # scale factor for recognition (0.5 = 2× faster)
```

Edit tolerance in `face_module/face_recognizer.py`:
```python
TOLERANCE = 0.55       # lower = stricter (fewer false positives)
```

---

## Dataset Links

| Dataset | URL | Use |
|---------|-----|-----|
| LFW (Labeled Faces in the Wild) | https://www.kaggle.com/datasets/jessicali9530/lfw-dataset | Face recognition |
| CASIA Gait Dataset B | https://www.kaggle.com/datasets/mohamedhanyyy/gaitb | Gait analysis |
| Face Recognition Dataset | https://www.kaggle.com/datasets/vasukipatel/face-recognition-dataset | Face recognition |

---

## Viva Preparation

**Q: What deep learning technique is used for face recognition?**
A: FaceNet-based deep convolutional network (via dlib) that maps each face to a 128-dimensional embedding vector. Matching uses Euclidean distance between embeddings.

**Q: How does gait detection work?**
A: Background subtraction (MOG2 algorithm) isolates moving foreground. Person contours are extracted and tracked frame-to-frame by centroid proximity. Speed and stride oscillation frequency classify the gait pattern.

**Q: What is the difference between face detection and recognition?**
A: Detection locates faces in the image (bounding box). Recognition identifies *who* the detected face belongs to by comparing its embedding to a database.

**Q: Which datasets were used?**
A: LFW (Labeled Faces in the Wild) for face recognition — 13,000+ labeled images of public figures. Custom webcam images for personalized recognition.

**Q: How is this suitable for real surveillance?**
A: The system processes each frame in real-time, handles multiple persons simultaneously, handles unknown person detection and logging. In a real deployment, camera feeds would be accessed over RTSP and the face database would be larger.

---

## Tech Stack Summary

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| GUI | Tkinter |
| Video capture | OpenCV |
| Face detection | Haar Cascade (OpenCV) |
| Face recognition | face_recognition (dlib/FaceNet) |
| Motion detection | MOG2 background subtraction |
| Gait analysis | Centroid tracking + signal analysis |
| Logging | CSV + in-memory |

---

## License

This project is for academic/educational purposes.
