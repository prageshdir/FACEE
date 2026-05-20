"""
Deep Learning Based Face and Gait Recognition Using Surveillance Camera
MCA Major Project

HOW TO RUN:
  1. Open Command Prompt (CMD)
  2. Go to this folder:  cd path\\to\\FACEE
  3. Install libraries:  pip install -r requirements.txt
  4. Run the app:        python app.py
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

from face_module import FaceDetector, FaceRecognizer
from gait_module import MotionDetector, GaitAnalyzer
from utils import RecognitionLogger, draw_box, draw_timestamp, save_screenshot


# ── Settings (change these if needed) ──────────────────────
CAMERA_INDEX   = 0      # 0 = first webcam, try 1 if webcam not found
LOG_COOLDOWN   = 4      # seconds between repeated log entries per person
# ────────────────────────────────────────────────────────────


class App(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Face & Gait Recognition — Surveillance System")
        self.configure(bg="#1a1a2e")
        self.geometry("1100x640")
        self.minsize(900, 580)
        self.protocol("WM_DELETE_WINDOW", self._quit)

        # AI modules
        self.detector   = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.motion     = MotionDetector()
        self.gait       = GaitAnalyzer()
        self.logger     = RecognitionLogger()

        # State
        self.cap            = None
        self.running        = False
        self.current_frame  = None        # latest annotated frame (BGR)
        self._last_log      = {}          # name -> last log time

        self._build_ui()
        self._refresh_log()

    # ─────────────────────────────────────────
    # UI Layout
    # ─────────────────────────────────────────

    def _build_ui(self):
        # ── Title bar ──
        bar = tk.Frame(self, bg="#16213e", pady=6)
        bar.pack(fill=tk.X)
        tk.Label(bar, text="  Face & Gait Surveillance System",
                 bg="#16213e", fg="#e2e2e2",
                 font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=8)

        self._persons_lbl = tk.Label(bar, text="Persons in DB: 0",
                                     bg="#16213e", fg="#4ecca3",
                                     font=("Segoe UI", 9))
        self._persons_lbl.pack(side=tk.RIGHT, padx=12)

        # ── Body: video feed (left) + controls (right) ──
        body = tk.Frame(self, bg="#1a1a2e")
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Right: controls + log — pack FIRST so it always gets its 220 px
        right = tk.Frame(body, bg="#1a1a2e", width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right.pack_propagate(False)

        self._build_buttons(right)
        self._build_log_panel(right)

        # Left: video — packed second; fills whatever space remains
        left = tk.Frame(body, bg="#1a1a2e")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Fixed-pixel container so the Label never uses character-unit sizing
        _video_frame = tk.Frame(left, bg="#000", width=640, height=480)
        _video_frame.pack()
        _video_frame.pack_propagate(False)
        self._canvas = tk.Label(_video_frame, bg="#000")
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._status = tk.StringVar(value="Camera is stopped.  Press  ▶ Start  to begin.")
        tk.Label(left, textvariable=self._status,
                 bg="#1a1a2e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(pady=(4, 0))

        # ── Footer ──
        tk.Label(self,
                 text="MCA Major Project  |  OpenCV + LBPH + MOG2",
                 bg="#1a1a2e", fg="#444466",
                 font=("Segoe UI", 8)).pack(pady=(0, 4))

    def _build_buttons(self, parent):
        tk.Label(parent, text="Controls",
                 bg="#1a1a2e", fg="#e2e2e2",
                 font=("Segoe UI", 10, "bold")).pack(pady=(4, 8))

        def btn(text, color, cmd, **kw):
            b = tk.Button(parent, text=text, bg=color, fg="#1a1a2e",
                          font=("Segoe UI", 9, "bold"),
                          relief=tk.FLAT, bd=0, pady=7, width=22,
                          command=cmd, **kw)
            b.pack(pady=3)
            return b

        self._btn_start = btn("▶  Start Camera",  "#4ecca3", self._start)
        self._btn_stop  = btn("■  Stop Camera",   "#ff6b6b", self._stop, state=tk.DISABLED)
        btn("📸  Register My Face",  "#ffd166", self._register_face)
        btn("💾  Screenshot",        "#a29bfe", self._screenshot)
        btn("🔄  Reload Face DB",    "#74b9ff", self._reload_db)
        btn("🗑  Clear Log",         "#636e72", self._clear_log)

        self._fps_lbl = tk.Label(parent, text="FPS: --",
                                 bg="#1a1a2e", fg="#ffd166",
                                 font=("Segoe UI", 9))
        self._fps_lbl.pack(pady=(10, 0))

    def _build_log_panel(self, parent):
        tk.Label(parent, text="Recognition Log",
                 bg="#1a1a2e", fg="#e2e2e2",
                 font=("Segoe UI", 10, "bold")).pack(pady=(14, 4))

        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_box = tk.Listbox(frame, yscrollcommand=sb.set,
                                   bg="#0f3460", fg="#e2e2e2",
                                   font=("Courier New", 8),
                                   relief=tk.FLAT, bd=0,
                                   selectmode=tk.SINGLE)
        self._log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self._log_box.yview)

    # ─────────────────────────────────────────
    # Camera thread
    # ─────────────────────────────────────────

    def _start(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # CAP_DSHOW faster on Windows
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error",
                                 f"Cannot open camera {CAMERA_INDEX}.\n\n"
                                 "• Make sure your webcam is plugged in.\n"
                                 "• Try changing CAMERA_INDEX = 1 in app.py")
            return

        self.running = True
        self._btn_start.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._status.set("Camera running…")

        # Run camera loop in a background thread so GUI doesn't freeze
        threading.Thread(target=self._camera_loop, daemon=True).start()
        self._show_frame()   # start GUI refresh loop

    def _stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self._btn_start.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        self._status.set("Camera stopped.")

    def _camera_loop(self):
        """Runs in background thread. Reads frames and runs AI."""
        fps_timer = time.time()
        frame_count = 0

        while self.running:
            if self.cap is None:
                break
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            # ── Step 1: Detect faces ──
            face_boxes = self.detector.detect(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ── Step 2: Recognize each face ──
            for (x, y, w, h) in face_boxes:
                face_crop = gray[y:y+h, x:x+w]          # crop grayscale face
                name, conf = self.recognizer.predict(face_crop)

                color = (50, 200, 50) if name != "Unknown" else (50, 50, 220)
                label = f"{name}  {conf}%"
                draw_box(frame, x, y, w, h, color, label)

                # Log (but not too often for same person)
                now = time.time()
                if now - self._last_log.get(name, 0) > LOG_COOLDOWN:
                    self._last_log[name] = now
                    self.logger.log(name, conf)

            # ── Step 3: Detect moving persons (gait) ──
            persons, _ = self.motion.detect(frame)
            gait_results = self.gait.update(persons)

            for g in gait_results:
                x, y, w, h = g["bbox"]
                gait_label = f"{g['label']}  {g['score']}%"
                # Orange box for gait tracking
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
                cv2.putText(frame, gait_label, (x, y + h + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 2)

            # ── Step 4: Overlay FPS + timestamp ──
            frame_count += 1
            elapsed = time.time() - fps_timer
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                fps_timer = time.time()
                self._fps_lbl.config(text=f"FPS: {fps:.1f}")

            draw_timestamp(frame)
            self.current_frame = frame.copy()

    def _show_frame(self):
        """Runs in GUI thread every 30ms — displays latest frame."""
        if self.running and self.current_frame is not None:
            rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self._canvas.imgtk = img      # hold reference to prevent GC
            self._canvas.config(image=img)
            self._persons_lbl.config(text=f"Persons in DB: {self.recognizer.person_count}")

        if self.running:
            self.after(30, self._show_frame)

    # ─────────────────────────────────────────
    # Button actions
    # ─────────────────────────────────────────

    def _register_face(self):
        """Capture current frame and save face to database."""
        if self.current_frame is None:
            messagebox.showwarning("No Frame", "Start the camera first, then click Register.")
            return

        name = simpledialog.askstring("Register Face", "Enter your name:")
        if not name or not name.strip():
            return
        name = name.strip().replace(" ", "_")

        # Detect face in current frame
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        boxes = self.detector.detect(self.current_frame)

        if not boxes:
            messagebox.showerror("No Face Found",
                                 "No face detected in the current frame.\n"
                                 "Make sure your face is clearly visible.")
            return

        # Use the first (largest) detected face
        x, y, w, h = max(boxes, key=lambda b: b[2] * b[3])
        face_crop = gray[y:y+h, x:x+w]

        ok, msg = self.recognizer.register_face(face_crop, name)
        if ok:
            messagebox.showinfo("Success! ✓", msg)
        else:
            messagebox.showerror("Failed", msg)

    def _screenshot(self):
        if self.current_frame is None:
            messagebox.showwarning("No Frame", "Start the camera first.")
            return
        path = save_screenshot(self.current_frame)
        messagebox.showinfo("Saved", f"Screenshot saved to:\n{path}")

    def _reload_db(self):
        self.recognizer.reload()
        messagebox.showinfo("Reloaded",
                            f"Face database reloaded.\n{self.recognizer.person_count} person(s) found.")

    def _clear_log(self):
        self.logger.recent.clear()
        self._log_box.delete(0, tk.END)

    def _refresh_log(self):
        """Update the log panel every 2 seconds."""
        self._log_box.delete(0, tk.END)
        for e in reversed(self.logger.recent):
            line = f"{e['time'][-8:]}  {e['name']:<14} {e['gait']}"
            self._log_box.insert(tk.END, line)
            color = "#ff6b6b" if e["name"] == "Unknown" else "#4ecca3"
            self._log_box.itemconfig(tk.END, fg=color)
        self.after(2000, self._refresh_log)

    def _quit(self):
        self._stop()
        self.destroy()


# ── Run the app ─────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
