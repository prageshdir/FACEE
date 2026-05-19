# Face & Gait Recognition — Surveillance System
### MCA Major Project

---

## HOW TO RUN ON WINDOWS (Step by Step)

### Step 1 — Download this project

If you downloaded a ZIP, extract it to a folder like:
```
C:\Users\YourName\Desktop\FACEE
```

---

### Step 2 — Open Command Prompt in the project folder

1. Open the `FACEE` folder in File Explorer
2. Click in the address bar at the top
3. Type `cmd` and press **Enter**
4. A black Command Prompt window opens in that folder

---

### Step 3 — Install the required libraries

Copy and paste this command into the Command Prompt, then press **Enter**:

```
pip install opencv-contrib-python numpy Pillow
```

Wait for it to finish (may take 1–2 minutes).

---

### Step 4 — Run the app

```
python app.py
```

A window will open with the camera feed and controls.

---

## HOW TO USE THE APP

### Start the camera
Click **▶ Start Camera** — your webcam turns on.

### Register your face (first time only)
1. Sit in front of the webcam
2. Click **📸 Register My Face**
3. Type your name and press OK
4. Your face is now saved — the app will recognize you next time

### What you will see on screen
| Box Color | Meaning |
|-----------|---------|
| Green box | Recognized person + name + confidence % |
| Red box   | Unknown person |
| Orange box | Detected moving person (gait tracking) |
| Cyan text | Walking / Running / Standing + score |

### Recognition Log
Every time a face is recognized, it is saved automatically to:
```
logs/recognition_log.csv
```
You can open this file in Excel.

---

## TROUBLESHOOTING

**"Cannot open camera" error**
- Make sure your webcam is plugged in
- Open `app.py` in Notepad and change `CAMERA_INDEX = 0` to `CAMERA_INDEX = 1`

**"ModuleNotFoundError" error**
- Run Step 3 again: `pip install opencv-contrib-python numpy Pillow`

**"AttributeError: module 'cv2.face' has no attribute 'LBPHFaceRecognizer_create'" error**
- You have the wrong OpenCV package. Run these two commands:
  ```
  pip uninstall opencv-python
  pip install opencv-contrib-python
  ```

**Python not recognized**
- Download Python from https://www.python.org/downloads/
- During install, check the box **"Add Python to PATH"**

**App opens but webcam is black/frozen**
- Try unplugging and replugging the webcam
- Close other apps using the camera (Zoom, Teams, etc.)

---

## PROJECT STRUCTURE

```
FACEE/
│
├── app.py                  ← Main file — run this
├── requirements.txt        ← Library list
│
├── face_module/
│   ├── face_detector.py    ← Detects face location (Haar Cascade)
│   └── face_recognizer.py  ← Recognizes who it is (LBPH algorithm)
│
├── gait_module/
│   ├── motion_detector.py  ← Detects moving persons (MOG2)
│   └── gait_analyzer.py    ← Classifies walking pattern
│
├── utils/
│   ├── logger.py           ← Saves recognition events to CSV
│   └── helpers.py          ← Drawing functions
│
├── dataset/
│   └── known_faces/        ← Your registered face photos go here
│
├── models/                 ← Trained model saved here automatically
├── logs/                   ← recognition_log.csv saved here
└── screenshots/            ← Screenshots saved here
```

---

## HOW IT WORKS (for viva)

### Face Detection
Uses **Haar Cascade** — a pre-trained classifier built into OpenCV.
It scans the frame at multiple scales looking for face-like patterns.

### Face Recognition
Uses **LBPH (Local Binary Pattern Histograms)** — also built into OpenCV.
- Each face is described as a pattern of pixel intensities
- When a new face appears, it compares the pattern to all stored faces
- Returns the closest match + a confidence score

### Gait Detection
Uses **MOG2 (Mixture of Gaussians)** background subtraction:
- Learns what the background looks like over 300 frames
- Anything that moves becomes a white blob in the foreground mask
- Blobs big enough to be a person are tracked frame-to-frame
- Speed of centroid movement determines: Standing / Walking / Running

---

## VIVA Q&A

**Q: What algorithm is used for face recognition?**
A: LBPH (Local Binary Pattern Histograms). It divides the face into small cells and creates a histogram of pixel patterns. Recognition is done by comparing histograms.

**Q: How does gait detection work without a special sensor?**
A: We use background subtraction (MOG2) to isolate moving foreground objects from a static camera. Human silhouettes are extracted using contour detection, then their centroid is tracked across frames. The speed and oscillation of the centroid classifies the gait.

**Q: What is the difference between detection and recognition?**
A: Detection finds WHERE a face is in the image (gives a bounding box). Recognition identifies WHO that face belongs to (gives a name and confidence score).

**Q: What datasets can be used?**
A: LFW (Labeled Faces in the Wild) from Kaggle for pre-labeled images. Or custom images captured via webcam using the Register button.

**Q: What is confidence score?**
A: LBPH gives a distance value — how different the detected face is from stored faces. We convert this to a percentage: 100% = perfect match, 0% = completely different.

---

## Libraries Used

| Library | Purpose | Install |
|---------|---------|---------|
| opencv-contrib-python | Face detection, recognition, motion | `pip install opencv-contrib-python` |
| numpy | Array operations | `pip install numpy` |
| Pillow | Display images in Tkinter GUI | `pip install Pillow` |
| tkinter | GUI window (built into Python) | already installed |
