"""
Face Detector — YuNet CNN (OpenCV DNN).
Falls back to Haar Cascade if the model cannot be downloaded.
"""

import os
import cv2
import urllib.request


_YUNET_URL  = ("https://media.githubusercontent.com/media/opencv/opencv_zoo"
               "/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx")
_YUNET_PATH = "models/face_detection_yunet_2023mar.onnx"
_MIN_BYTES  = 50_000   # real model is ~230 KB; LFS pointer is ~130 bytes


def _try_download(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        print("[FaceDetector] Downloading YuNet CNN model (~230 KB)…")
        urllib.request.urlretrieve(url, path)
        if os.path.getsize(path) < _MIN_BYTES:
            os.remove(path)
            return False
        print("[FaceDetector] YuNet model ready.")
        return True
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        print(f"[FaceDetector] Download failed ({e}). Using Haar fallback.")
        return False


class FaceDetector:
    def __init__(self):
        self._yunet = None
        self._yunet_size = (0, 0)

        if os.path.exists(_YUNET_PATH) and os.path.getsize(_YUNET_PATH) >= _MIN_BYTES:
            self._use_cnn = True
        else:
            self._use_cnn = _try_download(_YUNET_URL, _YUNET_PATH)

        if not self._use_cnn:
            print("[FaceDetector] Using Haar Cascade (classical).")
            self._haar = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        else:
            print("[FaceDetector] Using YuNet CNN detector.")
            self._haar = None

    def _get_yunet(self, w, h):
        if self._yunet is None or self._yunet_size != (w, h):
            self._yunet = cv2.FaceDetectorYN.create(
                _YUNET_PATH, "", (w, h),
                score_threshold=0.7,
                nms_threshold=0.3,
                top_k=50,
            )
            self._yunet_size = (w, h)
        return self._yunet

    def detect(self, frame):
        """Return list of (x, y, w, h) bounding boxes."""
        if self._use_cnn:
            return self._detect_yunet(frame)
        return self._detect_haar(frame)

    def _detect_yunet(self, frame):
        h, w = frame.shape[:2]
        det = self._get_yunet(w, h)
        _, faces = det.detect(frame)
        if faces is None:
            return []
        boxes = []
        for f in faces:
            x, y, bw, bh = int(f[0]), int(f[1]), int(f[2]), int(f[3])
            x, y = max(0, x), max(0, y)
            boxes.append((x, y, bw, bh))
        return boxes

    def _detect_haar(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._haar.detectMultiScale(gray, scaleFactor=1.1,
                                            minNeighbors=5, minSize=(50, 50))
        return faces.tolist() if len(faces) else []

    @property
    def backend(self):
        return "YuNet CNN" if self._use_cnn else "Haar Cascade"
