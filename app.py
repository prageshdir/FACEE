"""
Deep Learning Based Face and Gait Recognition Using Surveillance Camera
MCA Major Project

Main Application — Tkinter GUI + OpenCV camera pipeline
"""

import os
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

from face_module import FaceDetector, FaceRecognizer
from gait_module import MotionDetector, GaitAnalyzer
from utils import RecognitionLogger, draw_face_result, draw_timestamp, save_screenshot, resize_frame


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
WINDOW_TITLE = "Face & Gait Recognition — Surveillance System"
CAMERA_INDEX = 0          # 0 = built-in webcam, change for external camera
DISPLAY_WIDTH = 640
DISPLAY_HEIGHT = 480
LOG_INTERVAL = 3          # seconds between duplicate log entries per person
RECOGNITION_SCALE = 0.5   # scale down frame for faster recognition


# ──────────────────────────────────────────────
# Processing Pipeline
# ──────────────────────────────────────────────

class SurveillancePipeline:
    """Encapsulates all AI processing (runs in background thread)."""

    def __init__(self):
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer()
        self.motion_detector = MotionDetector()
        self.gait_analyzer = GaitAnalyzer()
        self.logger = RecognitionLogger()

        self._last_log_time = {}   # name -> last log timestamp
        self._result_lock = threading.Lock()
        self._latest_results = {
            "face_results": [],
            "gait_results": [],
            "fps": 0.0,
        }

    def process_frame(self, frame):
        """Run full detection + recognition pipeline on one frame."""
        t0 = time.time()

        # --- Face recognition on a down-scaled copy ---
        small = cv2.resize(frame, (0, 0), fx=RECOGNITION_SCALE, fy=RECOGNITION_SCALE)
        face_results = self.face_recognizer.recognize(small)

        # Scale bounding locations back to original size
        inv = 1.0 / RECOGNITION_SCALE
        scaled_face_results = []
        for r in face_results:
            top, right, bottom, left = r["location"]
            r["location"] = (
                int(top * inv), int(right * inv),
                int(bottom * inv), int(left * inv),
            )
            scaled_face_results.append(r)

        # --- Gait / motion detection ---
        persons, fg_mask = self.motion_detector.detect_persons(frame)
        gait_results = self.gait_analyzer.update(persons)

        fps = 1.0 / (time.time() - t0 + 1e-6)

        # --- Logging (throttled) ---
        now = time.time()
        for r in scaled_face_results:
            name = r["name"]
            last = self._last_log_time.get(name, 0)
            if now - last >= LOG_INTERVAL:
                gait_label = gait_results[0]["gait_label"] if gait_results else "N/A"
                gait_score = gait_results[0]["gait_score"] if gait_results else 0
                self.logger.log(name, r["confidence"], gait_label, gait_score)
                self._last_log_time[name] = now

        with self._result_lock:
            self._latest_results = {
                "face_results": scaled_face_results,
                "gait_results": gait_results,
                "fps": fps,
                "fg_mask": fg_mask,
            }
        return scaled_face_results, gait_results

    def get_latest_results(self):
        with self._result_lock:
            return dict(self._latest_results)


# ──────────────────────────────────────────────
# GUI Application
# ──────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.pipeline = SurveillancePipeline()
        self.cap = None
        self._running = False
        self._thread = None

        self._build_ui()
        self._update_log_panel()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ── Top bar ──
        top = tk.Frame(self, bg="#1e1e2e", pady=4)
        top.pack(fill=tk.X)
        tk.Label(
            top,
            text="  Face & Gait Surveillance System",
            bg="#1e1e2e", fg="#cdd6f4",
            font=("Helvetica", 14, "bold"),
        ).pack(side=tk.LEFT, padx=8)

        self._known_label = tk.Label(
            top, text="Known Persons: 0",
            bg="#1e1e2e", fg="#a6e3a1",
            font=("Helvetica", 10),
        )
        self._known_label.pack(side=tk.RIGHT, padx=12)

        # ── Main content (left = video, right = panel) ──
        main = tk.Frame(self, bg="#181825")
        main.pack(fill=tk.BOTH, expand=True)

        # Left: camera feed
        left_col = tk.Frame(main, bg="#181825")
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._video_canvas = tk.Label(left_col, bg="#000000")
        self._video_canvas.pack(fill=tk.BOTH, expand=True)

        self._status_var = tk.StringVar(value="Camera stopped")
        tk.Label(
            left_col, textvariable=self._status_var,
            bg="#181825", fg="#89b4fa",
            font=("Helvetica", 9),
        ).pack(pady=(2, 0))

        # Right: controls + log
        right_col = tk.Frame(main, bg="#181825", width=260)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=8)
        right_col.pack_propagate(False)

        self._build_controls(right_col)
        self._build_log_panel(right_col)

        # ── Bottom bar ──
        bottom = tk.Frame(self, bg="#1e1e2e", pady=3)
        bottom.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(
            bottom,
            text="MCA Major Project  |  Face & Gait Recognition",
            bg="#1e1e2e", fg="#6c7086",
            font=("Helvetica", 8),
        ).pack()

    def _build_controls(self, parent):
        tk.Label(
            parent, text="Controls", bg="#181825", fg="#cdd6f4",
            font=("Helvetica", 11, "bold"),
        ).pack(pady=(0, 6))

        btn_cfg = dict(width=22, font=("Helvetica", 9, "bold"), relief=tk.FLAT, bd=0, pady=6)

        self._btn_start = tk.Button(
            parent, text="▶  Start Camera",
            bg="#a6e3a1", fg="#1e1e2e",
            command=self._start_camera, **btn_cfg,
        )
        self._btn_start.pack(pady=3)

        self._btn_stop = tk.Button(
            parent, text="■  Stop Camera",
            bg="#f38ba8", fg="#1e1e2e",
            command=self._stop_camera, state=tk.DISABLED, **btn_cfg,
        )
        self._btn_stop.pack(pady=3)

        tk.Button(
            parent, text="📸  Register New Face",
            bg="#89dceb", fg="#1e1e2e",
            command=self._register_face, **btn_cfg,
        ).pack(pady=3)

        tk.Button(
            parent, text="💾  Save Screenshot",
            bg="#cba6f7", fg="#1e1e2e",
            command=self._save_screenshot, **btn_cfg,
        ).pack(pady=3)

        tk.Button(
            parent, text="🔄  Reload Face DB",
            bg="#fab387", fg="#1e1e2e",
            command=self._reload_db, **btn_cfg,
        ).pack(pady=3)

        tk.Button(
            parent, text="🗑️  Clear Log",
            bg="#6c7086", fg="#cdd6f4",
            command=self._clear_log, **btn_cfg,
        ).pack(pady=3)

        # FPS indicator
        self._fps_var = tk.StringVar(value="FPS: --")
        tk.Label(
            parent, textvariable=self._fps_var,
            bg="#181825", fg="#f9e2af",
            font=("Helvetica", 9),
        ).pack(pady=(8, 2))

    def _build_log_panel(self, parent):
        tk.Label(
            parent, text="Recognition Log",
            bg="#181825", fg="#cdd6f4",
            font=("Helvetica", 10, "bold"),
        ).pack(pady=(12, 4))

        frame = tk.Frame(parent, bg="#181825")
        frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self._log_list = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            bg="#313244", fg="#cdd6f4",
            font=("Courier", 8),
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            bd=0,
        )
        scrollbar.config(command=self._log_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Camera thread
    # ------------------------------------------------------------------

    def _start_camera(self):
        if self._running:
            return
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", f"Cannot open camera index {CAMERA_INDEX}.\n"
                                 "Check your webcam connection.")
            return
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, DISPLAY_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, DISPLAY_HEIGHT)

        self._running = True
        self._btn_start.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._status_var.set("Camera running…")

        self._thread = threading.Thread(target=self._camera_loop, daemon=True)
        self._thread.start()
        self._poll_frame()

    def _stop_camera(self):
        self._running = False
        self._btn_start.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        self._status_var.set("Camera stopped")
        if self.cap:
            self.cap.release()
            self.cap = None

    def _camera_loop(self):
        """Background thread: reads frames and runs AI pipeline."""
        while self._running:
            if self.cap is None or not self.cap.isOpened():
                break
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            face_results, gait_results = self.pipeline.process_frame(frame)

            # Annotate frame
            for r in face_results:
                draw_face_result(frame, r)
            for g in gait_results:
                x, y, w, h = g["bbox"]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 165, 0), 2)
                gait_text = f"{g['gait_label']} {g['gait_score']}%"
                cv2.putText(frame, gait_text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
            draw_timestamp(frame)

            # FPS overlay
            fps = self.pipeline.get_latest_results().get("fps", 0)
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Store annotated frame for GUI thread
            self._current_frame = frame

    def _poll_frame(self):
        """GUI thread: refresh canvas from latest processed frame."""
        if not self._running:
            return

        frame = getattr(self, "_current_frame", None)
        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self._video_canvas.imgtk = imgtk
            self._video_canvas.configure(image=imgtk)

            fps = self.pipeline.get_latest_results().get("fps", 0)
            self._fps_var.set(f"FPS: {fps:.1f}")
            self._known_label.config(
                text=f"Known Persons: {self.pipeline.face_recognizer.known_person_count}"
            )

        self.after(30, self._poll_frame)  # ~33 FPS GUI refresh

    # ------------------------------------------------------------------
    # Log panel refresh
    # ------------------------------------------------------------------

    def _update_log_panel(self):
        entries = self.pipeline.logger.recent(30)
        self._log_list.delete(0, tk.END)
        for e in entries:
            line = f"{e['timestamp'][-8:]}  {e['name']:<14} {e['gait']}"
            color = "#f38ba8" if e["name"] == "Unknown" else "#a6e3a1"
            self._log_list.insert(tk.END, line)
            self._log_list.itemconfig(tk.END, fg=color)
        self.after(2000, self._update_log_panel)  # refresh every 2s

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def _register_face(self):
        """Capture current frame and register a new person."""
        frame = getattr(self, "_current_frame", None)
        if frame is None:
            messagebox.showwarning("No Frame", "Start the camera first.")
            return
        name = simpledialog.askstring("Register Face", "Enter person's name:")
        if not name or not name.strip():
            return
        name = name.strip().replace(" ", "_")
        ok, msg = self.pipeline.face_recognizer.register_face(frame.copy(), name)
        if ok:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Failed", msg)

    def _save_screenshot(self):
        frame = getattr(self, "_current_frame", None)
        if frame is None:
            messagebox.showwarning("No Frame", "Start the camera first.")
            return
        path = save_screenshot(frame)
        messagebox.showinfo("Saved", f"Screenshot saved:\n{path}")

    def _reload_db(self):
        self.pipeline.face_recognizer.reload()
        count = self.pipeline.face_recognizer.known_person_count
        messagebox.showinfo("Reloaded", f"Face database reloaded.\n{count} person(s) loaded.")

    def _clear_log(self):
        self.pipeline.logger.clear_memory()
        self._log_list.delete(0, tk.END)

    def _on_close(self):
        self._stop_camera()
        self.destroy()


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
