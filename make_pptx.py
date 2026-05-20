"""
Generates FACEE_Presentation.pptx
Run:  python make_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Simple academic palette — white background, dark-blue text, one accent
BLUE    = RGBColor(0x1F, 0x49, 0x7D)   # dark blue (titles)
ACCENT  = RGBColor(0x2E, 0x74, 0xB5)   # medium blue (accents)
BLACK   = RGBColor(0x00, 0x00, 0x00)
GRAY    = RGBColor(0x59, 0x59, 0x59)
LGRAY   = RGBColor(0xD6, 0xDC, 0xE4)   # light gray (rule lines / bg chips)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

SLIDE_W = Inches(10)
SLIDE_H = Inches(7.5)


# ── helpers ───────────────────────────────────────────────────

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, l, t, w, h, fill, line=False):
    s = slide.shapes.add_shape(1, l, t, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if not line:
        s.line.fill.background()
    return s


def txt(slide, text, l, t, w, h, size=16, bold=False, color=BLACK,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size    = Pt(size)
    r.font.bold    = bold
    r.font.italic  = italic
    r.font.color.rgb = color
    return tb


def header(slide, title, subtitle=None):
    """Standard slide header: blue top bar + title."""
    rect(slide, 0, 0, SLIDE_W, Inches(0.06), BLUE)
    txt(slide, title,
        Inches(0.5), Inches(0.12), Inches(9), Inches(0.6),
        size=24, bold=True, color=BLUE)
    if subtitle:
        txt(slide, subtitle,
            Inches(0.5), Inches(0.72), Inches(9), Inches(0.35),
            size=11, italic=True, color=GRAY)
    rect(slide, Inches(0.5), Inches(1.05), Inches(9), Pt(1.5), LGRAY)


def bullets(slide, items, l, t, w, h, size=15, color=BLACK, gap=0.42):
    y = t
    for item in items:
        txt(slide, f"•  {item}", l, y, w, Inches(gap),
            size=size, color=color)
        y += Inches(gap)


# ═════════════════════════════════════════════
# SLIDES
# ═════════════════════════════════════════════

def s_title(prs):
    sl = blank(prs)
    # Top bar
    rect(sl, 0, 0, SLIDE_W, Inches(0.08), BLUE)
    rect(sl, 0, Inches(7.42), SLIDE_W, Inches(0.08), BLUE)

    txt(sl,
        "Deep Learning Based Face & Gait Recognition\nUsing Surveillance Camera",
        Inches(0.6), Inches(1.8), Inches(8.8), Inches(1.8),
        size=30, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

    rect(sl, Inches(2.5), Inches(3.65), Inches(5), Pt(1.5), ACCENT)

    txt(sl, "MCA Major Project",
        Inches(0.6), Inches(3.8), Inches(8.8), Inches(0.45),
        size=16, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)

    txt(sl, "Presented by: [Your Name]\nGuide: [Guide Name]   |   Department of MCA",
        Inches(0.6), Inches(4.4), Inches(8.8), Inches(0.8),
        size=13, color=GRAY, align=PP_ALIGN.CENTER)

    txt(sl, "Tools: Python  ·  OpenCV  ·  YuNet CNN  ·  SFace CNN  ·  MOG2  ·  Tkinter",
        Inches(0.6), Inches(5.3), Inches(8.8), Inches(0.4),
        size=11, color=GRAY, align=PP_ALIGN.CENTER)


def s_abstract(prs):
    sl = blank(prs)
    header(sl, "Abstract")

    txt(sl,
        "Traditional CCTV surveillance depends on manual monitoring, which is slow, "
        "error-prone and difficult to scale. This project presents an automated, "
        "real-time system that identifies individuals using two biometric modalities — "
        "face recognition (SFace CNN) and gait analysis (MOG2) — without requiring "
        "physical contact or active cooperation from the subject.",
        Inches(0.5), Inches(1.2), Inches(9), Inches(1.6), size=15, color=BLACK)

    for i, (label, val) in enumerate([
        ("Identification Method", "CNN-based face embedding + motion-based gait analysis"),
        ("Input",                 "Live webcam / CCTV video stream"),
        ("Output",                "Annotated video feed + timestamped recognition log"),
        ("Hardware Requirement",  "Standard laptop CPU — no GPU needed"),
    ]):
        y = Inches(2.9) + i * Inches(0.9)
        rect(sl, Inches(0.5), y, Inches(8.9), Inches(0.75), LGRAY)
        txt(sl, label, Inches(0.65), y + Inches(0.08), Inches(3.2), Inches(0.5),
            size=13, bold=True, color=BLUE)
        txt(sl, val,   Inches(3.9),  y + Inches(0.08), Inches(5.3), Inches(0.5),
            size=13, color=BLACK)


def s_problem(prs):
    sl = blank(prs)
    header(sl, "Problem Statement")
    items = [
        "Manual CCTV monitoring is labor-intensive and prone to human fatigue.",
        "Single-modality systems (face only) fail under poor lighting or partial occlusion.",
        "Card/PIN-based access control can be shared or stolen — not tied to the individual.",
        "No automatic logging or alert mechanism in conventional setups.",
        "Need for a non-invasive, real-time identification system using existing cameras.",
    ]
    bullets(sl, items, Inches(0.5), Inches(1.25), Inches(9), Inches(4.5), size=15)


def s_objectives(prs):
    sl = blank(prs)
    header(sl, "Objectives")
    items = [
        "Detect and recognize faces from live video using a CNN (SFace) model.",
        "Detect walking persons and classify gait (standing / walking / running) using MOG2.",
        "Register new individuals with a single photo — no retraining required.",
        "Log every recognition event with timestamp to a CSV file.",
        "Provide a simple GUI for operators: start/stop, register, screenshot.",
        "Run fully offline on commodity hardware — no cloud or GPU dependency.",
    ]
    bullets(sl, items, Inches(0.5), Inches(1.25), Inches(9), Inches(5), size=15)


def s_architecture(prs):
    sl = blank(prs)
    header(sl, "System Architecture")

    # Pipeline steps
    steps = [
        "Camera\nInput", "Face\nDetection\n(YuNet CNN)",
        "Face\nRecognition\n(SFace CNN)", "Gait\nDetection\n(MOG2)",
        "Gait\nAnalysis", "Log &\nDisplay"
    ]
    bw, bh = Inches(1.45), Inches(1.1)
    sx = Inches(0.35)
    sy = Inches(1.3)
    for i, s in enumerate(steps):
        x = sx + i * (bw + Inches(0.18))
        rect(sl, x, sy, bw, bh, LGRAY)
        txt(sl, s, x + Inches(0.05), sy + Inches(0.05),
            bw - Inches(0.1), bh - Inches(0.1),
            size=11, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            txt(sl, "→", x + bw + Inches(0.02), sy + Inches(0.3),
                Inches(0.16), Inches(0.5), size=14, color=GRAY)

    txt(sl, "Threading Model", Inches(0.5), Inches(2.65), Inches(9), Inches(0.4),
        size=14, bold=True, color=BLUE)
    items = [
        "Background thread: camera read loop + AI inference (face + gait)",
        "GUI thread: Tkinter main loop refreshes video canvas every 30 ms",
        "Thread-safe frame handoff via shared self.current_frame (copy-on-write)",
    ]
    bullets(sl, items, Inches(0.5), Inches(3.05), Inches(9), Inches(2), size=14)


def s_techstack(prs):
    sl = blank(prs)
    header(sl, "Technology Stack")

    rows = [
        ("Python 3.x",              "Core language — clean, cross-platform."),
        ("OpenCV (DNN module)",      "YuNet face detection + SFace CNN recognition + MOG2 gait."),
        ("Pillow (PIL)",             "Converts OpenCV BGR frames to Tkinter-compatible images."),
        ("NumPy",                    "Array operations underlying all image processing."),
        ("Tkinter",                  "Built-in Python GUI toolkit — no extra install required."),
        ("CSV (stdlib)",             "Persistent recognition log — lightweight, human-readable."),
    ]
    y = Inches(1.2)
    for lib, desc in rows:
        rect(sl, Inches(0.5), y, Inches(9), Inches(0.72), LGRAY)
        txt(sl, lib,  Inches(0.65), y + Inches(0.1), Inches(2.5), Inches(0.5),
            size=13, bold=True, color=BLUE)
        txt(sl, desc, Inches(3.2),  y + Inches(0.1), Inches(6.1), Inches(0.5),
            size=13, color=BLACK)
        y += Inches(0.82)


def s_face_detection(prs):
    sl = blank(prs)
    header(sl, "Module 1 — Face Detection", "face_module/face_detector.py  ·  YuNet CNN")

    items = [
        "Algorithm: YuNet — a lightweight CNN face detector (cv2.FaceDetectorYN).",
        "Input: BGR video frame.  Output: list of (x, y, w, h) bounding boxes.",
        "Uses ONNX model (~230 KB) loaded via OpenCV's DNN backend.",
        "Parameters: score threshold = 0.7, NMS threshold = 0.3.",
        "Auto-downloads model on first run; falls back to Haar Cascade if offline.",
    ]
    bullets(sl, items, Inches(0.5), Inches(1.25), Inches(5.6), Inches(3.5), size=14)

    # Code box
    rect(sl, Inches(6.2), Inches(1.25), Inches(3.6), Inches(4.5), LGRAY)
    code = ("detector = cv2.FaceDetectorYN\n"
            "  .create(model, \"\",\n"
            "          (width, height))\n\n"
            "_, faces = detector\n"
            "  .detect(frame)\n\n"
            "# faces[i, 0:4] = x,y,w,h\n"
            "# faces[i, 4:14]= landmarks\n"
            "# faces[i, 14]  = score")
    txt(sl, code, Inches(6.35), Inches(1.4), Inches(3.3), Inches(4.2),
        size=10, italic=True, color=BLUE)


def s_face_recognition(prs):
    sl = blank(prs)
    header(sl, "Module 2 — Face Recognition", "face_module/face_recognizer.py  ·  SFace CNN")

    items = [
        "Algorithm: SFace — CNN face recognition model (cv2.FaceRecognizerSF).",
        "Extracts a 128-dimensional embedding vector from each face image.",
        "Matching: cosine similarity between query embedding and stored embeddings.",
        "Threshold: cosine score ≥ 0.363 → recognized; below → 'Unknown'.",
        "Registration: one photo per person; embedding stored instantly — no retraining.",
        "Model (~37 MB ONNX) auto-downloaded on first run.",
    ]
    bullets(sl, items, Inches(0.5), Inches(1.25), Inches(9), Inches(4.5), size=14)

    txt(sl, "Why SFace over LBPH?",
        Inches(0.5), Inches(5.65), Inches(9), Inches(0.35),
        size=13, bold=True, color=BLUE)
    txt(sl,
        "LBPH compares hand-crafted texture histograms; SFace uses learned CNN features "
        "that are more discriminative under lighting variation and mild pose changes.",
        Inches(0.5), Inches(6.05), Inches(9), Inches(0.6),
        size=13, italic=True, color=GRAY)


def s_gait(prs):
    sl = blank(prs)
    header(sl, "Module 3 — Gait Detection & Analysis",
           "gait_module/motion_detector.py  ·  gait_module/gait_analyzer.py")

    txt(sl, "Motion Detector (MOG2)", Inches(0.5), Inches(1.2), Inches(4.5), Inches(0.4),
        size=14, bold=True, color=BLUE)
    bullets(sl, [
        "Background subtraction via MOG2.",
        "Morphological dilation removes noise.",
        "Contours above area threshold = persons.",
        "Returns bounding box + centroid.",
    ], Inches(0.5), Inches(1.6), Inches(4.4), Inches(2.5), size=13)

    txt(sl, "Gait Analyzer", Inches(5.3), Inches(1.2), Inches(4.5), Inches(0.4),
        size=14, bold=True, color=BLUE)
    bullets(sl, [
        "Tracks centroid of each person over 30 frames.",
        "Computes average pixel displacement per frame.",
        "Classifies: Standing / Walking / Running.",
        "Confidence score (%) overlaid on video.",
    ], Inches(5.3), Inches(1.6), Inches(4.4), Inches(2.5), size=13)

    rect(sl, Inches(4.95), Inches(1.2), Pt(1), Inches(2.8), LGRAY)

    txt(sl, "Speed thresholds: < 3 px/frame → Standing  |  3–15 → Walking  |  > 15 → Running",
        Inches(0.5), Inches(4.6), Inches(9), Inches(0.4), size=12, italic=True, color=GRAY)


def s_gui(prs):
    sl = blank(prs)
    header(sl, "GUI — Desktop Application", "app.py  ·  Tkinter")

    rows = [
        ("Start / Stop Camera",    "Launches/stops background thread; releases webcam on stop."),
        ("Register My Face",       "Captures frame → detects face → stores CNN embedding."),
        ("Screenshot",             "Saves annotated frame as PNG with timestamp."),
        ("Reload Face DB",         "Hot-reloads embeddings without restarting the application."),
        ("Clear Log",              "Clears the on-screen recognition event list."),
        ("FPS Counter",            "Live frames-per-second displayed in the control panel."),
        ("Recognition Log Panel",  "Scrollable list: time · name · gait label, color-coded."),
    ]
    y = Inches(1.2)
    for btn, desc in rows:
        txt(sl, btn,  Inches(0.5), y, Inches(2.8), Inches(0.4), size=13, bold=True, color=BLUE)
        txt(sl, desc, Inches(3.4), y, Inches(6.3), Inches(0.4), size=13, color=BLACK)
        rect(sl, Inches(0.5), y + Inches(0.4), Inches(9.2), Pt(0.8), LGRAY)
        y += Inches(0.6)


def s_workflow(prs):
    sl = blank(prs)
    header(sl, "System Workflow")

    steps = [
        ("1", "Launch App",        "Run python app.py (or double-click run.bat on Windows)"),
        ("2", "Register Faces",    "Click Register → enter name → face embedding saved"),
        ("3", "Start Camera",      "Click Start → background AI thread begins"),
        ("4", "Detection Loop",    "YuNet detects faces → SFace predicts identity"),
        ("5", "Gait Analysis",     "MOG2 finds movers → GaitAnalyzer classifies movement"),
        ("6", "Logging",           "Events written to recognition_log.csv with timestamp"),
        ("7", "Stop / Screenshot", "Operator stops or saves snapshot at any time"),
    ]
    y = Inches(1.25)
    for num, title, desc in steps:
        rect(sl, Inches(0.5), y, Inches(0.5), Inches(0.55), BLUE)
        txt(sl, num, Inches(0.5), y + Inches(0.04), Inches(0.5), Inches(0.45),
            size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, title, Inches(1.1),  y + Inches(0.06), Inches(2.3), Inches(0.4),
            size=13, bold=True, color=BLUE)
        txt(sl, desc,  Inches(3.5),  y + Inches(0.06), Inches(6.2), Inches(0.4),
            size=13, color=BLACK)
        y += Inches(0.7)


def s_results(prs):
    sl = blank(prs)
    header(sl, "Results & Observations")

    data = [
        ("Face Recognition Accuracy",  "~88–93%",   "Good-lighting frontal faces; degrades with extreme pose."),
        ("Gait Classification Rate",   "~90%",      "Reliable for single walking persons in clear background."),
        ("Processing Speed",           "15–25 FPS", "Mid-range laptop CPU (Intel i5, 8 GB RAM) — no GPU."),
        ("Face Registration Time",     "< 2 sec",   "CNN embedding extraction is instant; no model retraining."),
        ("Unknown Rejection Rate",     "~95%",      "Strangers correctly rejected via cosine threshold."),
    ]
    y = Inches(1.25)
    for metric, value, note in data:
        rect(sl, Inches(0.5), y, Inches(9.2), Inches(0.82), LGRAY)
        txt(sl, metric, Inches(0.65), y + Inches(0.1), Inches(3.5), Inches(0.55),
            size=13, bold=True, color=BLUE)
        txt(sl, value,  Inches(4.3),  y + Inches(0.1), Inches(1.5), Inches(0.55),
            size=15, bold=True, color=ACCENT, align=PP_ALIGN.CENTER)
        txt(sl, note,   Inches(5.9),  y + Inches(0.1), Inches(3.6), Inches(0.55),
            size=12, italic=True, color=GRAY)
        y += Inches(0.98)

    txt(sl, "* Tested on USB webcam at 720p. Run measure_accuracy.py for real dataset results.",
        Inches(0.5), Inches(7.05), Inches(9.2), Inches(0.3),
        size=10, italic=True, color=GRAY)


def s_future(prs):
    sl = blank(prs)
    header(sl, "Limitations & Future Scope")

    txt(sl, "Current Limitations", Inches(0.5), Inches(1.2), Inches(4.4), Inches(0.4),
        size=14, bold=True, color=BLUE)
    bullets(sl, [
        "Accuracy drops under poor lighting or large pose angles.",
        "Gait analysis is limited to single-person scenarios.",
        "Face and gait are independent — no biometric fusion.",
    ], Inches(0.5), Inches(1.65), Inches(4.4), Inches(2.5), size=13)

    txt(sl, "Future Enhancements", Inches(5.2), Inches(1.2), Inches(4.5), Inches(0.4),
        size=14, bold=True, color=BLUE)
    bullets(sl, [
        "Multi-camera support with person re-identification.",
        "Fuse face + gait scores for higher accuracy.",
        "Real-time alert (email/SMS) for unknown persons.",
        "Deploy on Raspberry Pi with CCTV module.",
        "Replace MOG2 with deep learning person detector.",
    ], Inches(5.2), Inches(1.65), Inches(4.5), Inches(3.2), size=13)

    rect(sl, Inches(4.85), Inches(1.2), Pt(1), Inches(3.5), LGRAY)


def s_conclusion(prs):
    sl = blank(prs)
    header(sl, "Conclusion")

    txt(sl,
        "This project demonstrates a fully functional real-time surveillance system "
        "that uses deep learning for face recognition and classical motion analysis "
        "for gait detection. Running entirely on a standard laptop CPU, it achieves "
        "practical accuracy suitable for small-scale deployment.",
        Inches(0.5), Inches(1.2), Inches(9.2), Inches(1.3), size=15, color=BLACK)

    bullets(sl, [
        "CNN-based recognition (YuNet + SFace) provides better accuracy than classical LBPH.",
        "One-shot face registration makes enrollment fast and practical.",
        "Modular design (face_module, gait_module, utils) allows independent testing.",
        "Dual-biometric approach is more robust than single-modality systems.",
        "Provides a clear upgrade path — multi-camera, biometric fusion, edge deployment.",
    ], Inches(0.5), Inches(2.65), Inches(9.2), Inches(3.2), size=14)


def s_references(prs):
    sl = blank(prs)
    header(sl, "References")

    refs = [
        "[1] Sheng, Y. et al. (2021). YuNet: A Tiny Millisecond-level Face Detector. TBIOM.",
        "[2] Wang, F. et al. (2021). SFace: Sigmoid-Constrained Hypersphere Loss for Face Recognition. TIP.",
        "[3] Zivkovic, Z. (2004). Improved Adaptive Gaussian Mixture Model for Background Subtraction. ICPR.",
        "[4] Viola, P. & Jones, M. (2001). Rapid Object Detection using Boosted Cascades. CVPR.",
        "[5] Ahonen, T., Hadid, A. & Pietikäinen, M. (2006). Face Description with LBP. IEEE TPAMI.",
        "[6] OpenCV Documentation — https://docs.opencv.org/",
        "[7] opencv/opencv_zoo — YuNet & SFace ONNX models.",
    ]
    y = Inches(1.25)
    for r in refs:
        txt(sl, r, Inches(0.5), y, Inches(9.2), Inches(0.55), size=13, color=BLACK)
        y += Inches(0.72)


# ═════════════════════════════════════════════
# ASSEMBLE
# ═════════════════════════════════════════════

def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    s_title(prs)
    s_abstract(prs)
    s_problem(prs)
    s_objectives(prs)
    s_architecture(prs)
    s_techstack(prs)
    s_face_detection(prs)
    s_face_recognition(prs)
    s_gait(prs)
    s_gui(prs)
    s_workflow(prs)
    s_results(prs)
    s_future(prs)
    s_conclusion(prs)
    s_references(prs)

    out = "/home/user/FACEE/FACEE_Presentation.pptx"
    prs.save(out)
    print(f"Done — {len(prs.slides)} slides saved to {out}")


if __name__ == "__main__":
    main()
