"""
Generates Progress_2_Presentation.pptx
Matches the original SMIT Progress-2 format with updated content.
Run:  python make_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ── Palette (matches standard academic blue theme) ────────────
TITLE_BLUE  = RGBColor(0x1F, 0x49, 0x7D)
ACC_BLUE    = RGBColor(0x2E, 0x74, 0xB5)
BLACK       = RGBColor(0x00, 0x00, 0x00)
GRAY        = RGBColor(0x40, 0x40, 0x40)
LGRAY       = RGBColor(0xD6, 0xDC, 0xE4)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
GREEN       = RGBColor(0x37, 0x86, 0x10)
RED         = RGBColor(0xC0, 0x00, 0x00)

FOOTER_TEXT = "Dept. of Computer Application, SMIT, Majhitar, East Sikkim"

SLIDE_W = Inches(10)
SLIDE_H = Inches(7.5)


# ══════════════════════════════════════════════════════════════
# LOW-LEVEL HELPERS
# ══════════════════════════════════════════════════════════════

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, l, t, w, h, fill):
    s = slide.shapes.add_shape(1, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.fill.background()
    return s


def txt(slide, text, l, t, w, h, size=14, bold=False, color=BLACK,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run()
    run.text = text; run.font.size = Pt(size)
    run.font.bold = bold; run.font.italic = italic
    run.font.color.rgb = color
    return tb


def add_bullet_para(tf, text, size=13, color=BLACK, level=0, bold=False):
    p = tf.add_paragraph()
    p.level = level
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return p


def bullet_box(slide, items, l, t, w, h, size=13, color=BLACK, gap=None):
    """Simple bullet textbox — each item on its own paragraph."""
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()
        run = p.add_run()
        run.text = f"•  {item}"
        run.font.size = Pt(size)
        run.font.color.rgb = color
    return tb


# ── Standard slide chrome ─────────────────────────────────────

def add_footer(slide, num):
    """Blue bottom bar with institution name and slide number."""
    rect(slide, 0, Inches(7.1), SLIDE_W, Inches(0.4), ACC_BLUE)
    txt(slide, FOOTER_TEXT,
        Inches(0.2), Inches(7.12), Inches(8.5), Inches(0.35),
        size=10, color=WHITE, align=PP_ALIGN.LEFT)
    txt(slide, str(num),
        Inches(9.4), Inches(7.12), Inches(0.5), Inches(0.35),
        size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)


def slide_title_bar(slide, title, subtitle=None):
    """Blue top bar + title + optional subtitle."""
    rect(slide, 0, 0, SLIDE_W, Inches(0.06), ACC_BLUE)
    txt(slide, title,
        Inches(0.4), Inches(0.12), Inches(9.2), Inches(0.65),
        size=24, bold=True, color=TITLE_BLUE)
    if subtitle:
        txt(slide, subtitle,
            Inches(0.4), Inches(0.75), Inches(9.2), Inches(0.3),
            size=11, italic=True, color=GRAY)
    rect(slide, Inches(0.4), Inches(1.0), Inches(9.2), Pt(1.5), LGRAY)


# ══════════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ══════════════════════════════════════════════════════════════

def s_title(prs, num):
    sl = blank(prs)
    # Background
    rect(sl, 0, 0, SLIDE_W, Inches(0.08), ACC_BLUE)
    rect(sl, 0, Inches(7.42), SLIDE_W, Inches(0.08), ACC_BLUE)
    rect(sl, 0, Inches(2.8), SLIDE_W, Inches(0.04), LGRAY)
    rect(sl, 0, Inches(5.1), SLIDE_W, Inches(0.04), LGRAY)

    txt(sl,
        "Major Project Progress II Presentation\non\nDeep Learning Approaches For\nFace & Gait Recognition",
        Inches(0.6), Inches(0.9), Inches(8.8), Inches(1.9),
        size=26, bold=True, color=TITLE_BLUE, align=PP_ALIGN.CENTER)

    txt(sl, "Presented by",
        Inches(0.6), Inches(3.0), Inches(8.8), Inches(0.35),
        size=13, color=GRAY, align=PP_ALIGN.CENTER)
    txt(sl, "Afsana Chettri  ( 202422018 )",
        Inches(0.6), Inches(3.35), Inches(8.8), Inches(0.4),
        size=15, bold=True, color=BLACK, align=PP_ALIGN.CENTER)

    txt(sl, "Under the Guidance of",
        Inches(0.6), Inches(3.9), Inches(8.8), Inches(0.35),
        size=12, color=GRAY, align=PP_ALIGN.CENTER)
    txt(sl, "Mr. Simanta Kalita,  Assistance Professor, SMIT",
        Inches(0.6), Inches(4.25), Inches(8.8), Inches(0.35),
        size=13, bold=True, color=BLACK, align=PP_ALIGN.CENTER)
    txt(sl, "External Guide:  Mr. Sachin Manger,  Senior Faculty",
        Inches(0.6), Inches(4.6), Inches(8.8), Inches(0.35),
        size=13, bold=True, color=BLACK, align=PP_ALIGN.CENTER)

    txt(sl, FOOTER_TEXT,
        Inches(0.6), Inches(5.25), Inches(8.8), Inches(0.35),
        size=11, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
    txt(sl, str(num),
        Inches(9.4), Inches(7.12), Inches(0.5), Inches(0.35),
        size=10, bold=True, color=GRAY, align=PP_ALIGN.CENTER)


def s_contents(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Contents")
    add_footer(sl, num)

    items_l = [
        "Introduction",
        "Overview of the Problem",
        "Aim and Objectives",
        "Literature Survey",
        "Problem Definition",
        "Proposed Solution Strategy",
    ]
    items_r = [
        "H/W & S/W Requirements",
        "Team Structure  &  Gantt Chart",
        "System Architecture",
        "Modules Implemented",
        "Progress Summary",
        "Results,  Conclusion  &  References",
    ]
    nums_l = list(range(1, 7))
    nums_r = list(range(7, 13))

    for i, (item, n) in enumerate(zip(items_l, nums_l)):
        y = Inches(1.15) + i * Inches(0.82)
        txt(sl, str(n), Inches(0.4), y, Inches(0.4), Inches(0.6),
            size=14, bold=True, color=ACC_BLUE)
        txt(sl, item, Inches(0.85), y, Inches(4.0), Inches(0.6), size=13, color=BLACK)

    for i, (item, n) in enumerate(zip(items_r, nums_r)):
        y = Inches(1.15) + i * Inches(0.82)
        txt(sl, str(n), Inches(5.1), y, Inches(0.4), Inches(0.6),
            size=14, bold=True, color=ACC_BLUE)
        txt(sl, item, Inches(5.55), y, Inches(4.2), Inches(0.6), size=13, color=BLACK)

    rect(sl, Inches(4.85), Inches(1.1), Pt(1), Inches(5.8), LGRAY)


def s_introduction(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Introduction")
    add_footer(sl, num)
    items = [
        "Project develops a deep learning-based real-time surveillance system using face and gait recognition.",
        "Traditional systems rely only on face recognition, which fails in poor lighting, occlusions, or mask usage.",
        "Gait recognition is added because walking patterns are unique and hard to hide.",
        "Uses deep learning models (CNNs) to extract facial features and motion patterns from video streams.",
        "Combining both methods improves accuracy, reliability, and robustness in dynamic environments.",
        "The system is implemented as a desktop application that runs in real-time on standard hardware.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(9.2), Inches(5.5), size=14)


def s_overview(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "General Overview Of The Problem")
    add_footer(sl, num)
    items = [
        "Traditional security systems often rely only on face recognition, which may fail when faces are covered or unclear.",
        "People can avoid identification using masks, low lighting, or unfavorable camera angles.",
        "Security systems need a more reliable method to identify individuals across different situations.",
        "Combining face recognition with gait (walking style) recognition improves identification accuracy.",
        "A dual-biometric system is harder to deceive since both modalities must be simultaneously obscured.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(9.2), Inches(5.5), size=14)


def s_objectives_primary(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Aim and Objectives")
    add_footer(sl, num)

    txt(sl,
        "The main aim is to develop a real-time deep learning surveillance system combining face and "
        "gait recognition for accurate human identification under varying conditions.",
        Inches(0.4), Inches(1.1), Inches(9.2), Inches(0.9), size=13, color=BLACK)

    txt(sl, "Primary Objectives:", Inches(0.4), Inches(2.05), Inches(9.2), Inches(0.4),
        size=14, bold=True, color=TITLE_BLUE)
    items = [
        "Develop a real-time surveillance system combining face and gait recognition.",
        "Build a CNN-based face recognition module (SFace) to identify individuals from live video.",
        "Implement gait recognition based on walking patterns using MOG2 background subtraction.",
        "Integrate both modalities into a unified application for improved accuracy.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(2.45), Inches(9.2), Inches(3.5), size=13)


def s_objectives_secondary(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Aim and Objectives (Continued)")
    add_footer(sl, num)

    txt(sl, "Secondary Objectives:", Inches(0.4), Inches(1.1), Inches(9.2), Inches(0.4),
        size=14, bold=True, color=TITLE_BLUE)
    items = [
        "Study deep learning methods (CNNs, feature embeddings) for biometric recognition.",
        "Enable real-time video processing at 15–25 FPS on standard laptop hardware.",
        "Improve robustness under challenging conditions (low light, occlusion, pose variation).",
        "Evaluate accuracy using cosine similarity thresholds and leave-one-out cross-validation.",
        "Design the system for practical security applications (campus access, office surveillance).",
        "Run fully offline on commodity hardware without requiring a GPU or cloud services.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.55), Inches(9.2), Inches(5.0), size=13)


def s_feasibility(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Feasibility Study")
    add_footer(sl, num)

    sections = [
        ("Technical Feasibility",
         ["Uses OpenCV DNN module with ONNX-format CNN models (YuNet, SFace).",
          "OpenCV 4.5+ supports FaceDetectorYN and FaceRecognizerSF on CPU.",
          "Python + Tkinter provide a complete cross-platform desktop solution."]),
        ("Economic Feasibility",
         ["All libraries used are open-source and free (OpenCV, Python, Tkinter).",
          "No GPU or cloud subscription required — runs on existing hardware."]),
        ("Operational Feasibility",
         ["Single-click launcher (run.bat) for Windows users.",
          "One-shot face registration — no manual dataset labeling needed."]),
        ("Legal & Ethical Feasibility",
         ["Face data stored locally; no cloud upload or third-party processing.",
          "System is intended for consented institutional surveillance only."]),
    ]

    y = Inches(1.1)
    for title, pts in sections:
        txt(sl, title, Inches(0.4), y, Inches(9.2), Inches(0.38),
            size=13, bold=True, color=ACC_BLUE)
        y += Inches(0.38)
        for pt in pts:
            txt(sl, f"    –  {pt}", Inches(0.4), y, Inches(9.2), Inches(0.35),
                size=12, color=BLACK)
            y += Inches(0.35)
        y += Inches(0.1)


def s_literature(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Literature Survey")
    add_footer(sl, num)

    txt(sl, "Table 1: Literature Survey",
        Inches(0.4), Inches(1.05), Inches(9.2), Inches(0.3),
        size=11, italic=True, color=GRAY)

    headers = ["Author(s)", "Year", "Method", "Findings"]
    col_w   = [Inches(2.8), Inches(0.7), Inches(3.0), Inches(2.6)]
    rows = [
        ("Pundir & Sharma",          "2023", "CNN review for gait",         "Deep CNN outperforms traditional methods for gait recognition."),
        ("Sepas-Moghaddam & Etemad", "2022", "Deep gait survey",            "CNN+RNN fusion achieves best cross-view gait accuracy."),
        ("Sheng et al.",             "2021", "YuNet face detector",         "Lightweight CNN detector; <1 ms per frame on CPU."),
        ("Wang et al.",              "2021", "SFace embedding CNN",         "Sigmoid-constrained loss improves face embedding discriminability."),
        ("Viola & Jones",            "2001", "Haar Cascade detection",      "Fast classical face detector; baseline for comparison."),
    ]

    # header row
    x = Inches(0.35)
    y = Inches(1.38)
    rh = Inches(0.42)
    for j, (hdr, cw) in enumerate(zip(headers, col_w)):
        rect(sl, x, y, cw, rh, ACC_BLUE)
        txt(sl, hdr, x + Inches(0.05), y + Inches(0.06), cw - Inches(0.1), rh,
            size=11, bold=True, color=WHITE)
        x += cw

    for i, row in enumerate(rows):
        x = Inches(0.35)
        y2 = y + rh + i * rh
        bg = LGRAY if i % 2 == 0 else WHITE
        for j, (cell, cw) in enumerate(zip(row, col_w)):
            rect(sl, x, y2, cw, rh, bg)
            txt(sl, cell, x + Inches(0.05), y2 + Inches(0.05),
                cw - Inches(0.1), rh - Inches(0.05), size=10, color=BLACK)
            x += cw


def s_problem_definition(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Problem Definition")
    add_footer(sl, num)
    items = [
        "Traditional surveillance systems rely mainly on face recognition, which is not always reliable.",
        "Identification fails under poor lighting, masks, or occluded / angled faces.",
        "Changes in appearance (hairstyle, accessories) reduce recognition accuracy.",
        "There is no automatic alert or logging mechanism in basic surveillance setups.",
        "Combining face and gait biometrics provides a more robust and deception-resistant solution.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(9.2), Inches(5.5), size=14)


def s_proposed_solution(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Proposed Solution Strategy")
    add_footer(sl, num)
    items = [
        "Implement a CNN-based face detection module using YuNet (cv2.FaceDetectorYN) via OpenCV DNN.",
        "Implement a CNN-based face recognition module using SFace (cv2.FaceRecognizerSF) with cosine similarity matching.",
        "Implement gait analysis using MOG2 background subtraction to track and classify walking patterns.",
        "Fuse both recognition results in a unified desktop GUI built with Python Tkinter.",
        "Auto-download pre-trained ONNX models on first run — no manual setup required.",
        "Log every recognition event (name, confidence, gait label, timestamp) to a CSV file for audit.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(9.2), Inches(5.5), size=13)


def s_requirements(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "H/W & S/W Requirements")
    add_footer(sl, num)

    txt(sl, "Hardware Requirements:", Inches(0.4), Inches(1.1), Inches(4.4), Inches(0.4),
        size=14, bold=True, color=TITLE_BLUE)
    hw = ["Personal computer or laptop",
          "Minimum 8 GB RAM",
          "Intel i5 processor or equivalent",
          "USB webcam or built-in camera",
          "Stable internet connection (for initial model download)"]
    bullet_box(sl, hw, Inches(0.4), Inches(1.5), Inches(4.4), Inches(3.0), size=13)

    txt(sl, "Software Requirements:", Inches(5.2), Inches(1.1), Inches(4.4), Inches(0.4),
        size=14, bold=True, color=TITLE_BLUE)
    sw = ["Operating System: Windows 10/11 or Linux",
          "Python 3.8+",
          "OpenCV (opencv-contrib-python ≥ 4.5)",
          "Pillow (PIL)  &  NumPy",
          "Tkinter (built-in with Python)"]
    bullet_box(sl, sw, Inches(5.2), Inches(1.5), Inches(4.4), Inches(3.0), size=13)

    rect(sl, Inches(4.85), Inches(1.1), Pt(1), Inches(4.5), LGRAY)


def s_team(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Project Plan — Team Structure")
    add_footer(sl, num)

    boxes = [
        (Inches(0.6),  Inches(1.5), "Internal Guide\nMr. Simanta Kalita\nAssistance Professor, SMIT"),
        (Inches(3.85), Inches(1.5), "External Guide\nMr. Sachin Manger\nSenior Faculty"),
        (Inches(3.85), Inches(4.0), "Student\nAfsana Chettri\n( 202422018 )"),
    ]
    for x, y, label in boxes:
        rect(sl, x, y, Inches(2.5), Inches(1.6), LGRAY)
        txt(sl, label, x + Inches(0.1), y + Inches(0.15), Inches(2.3), Inches(1.3),
            size=13, bold=False, color=TITLE_BLUE, align=PP_ALIGN.CENTER)

    txt(sl, "Fig 1: Team Structure",
        Inches(0.4), Inches(6.55), Inches(9.2), Inches(0.3),
        size=10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)


def s_gantt(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Gantt Chart")
    add_footer(sl, num)
    txt(sl, "Table 2: Gantt Chart",
        Inches(0.4), Inches(1.05), Inches(9.2), Inches(0.3),
        size=11, italic=True, color=GRAY)

    phases = [
        ("Phase 1: Literature Review & Planning",    "Aug – Sep 2024",  True),
        ("Phase 2: System Design & Architecture",    "Oct 2024",        True),
        ("Phase 3: Face Detection Module (YuNet)",   "Nov 2024",        True),
        ("Phase 4: Face Recognition Module (SFace)", "Nov – Dec 2024",  True),
        ("Phase 5: Gait Detection Module (MOG2)",    "Dec 2024",        True),
        ("Phase 6: GUI Integration & Testing",       "Jan 2025",        True),
        ("Phase 7: Accuracy Measurement",            "Feb 2025",        True),
        ("Phase 8: Final Report & Presentation",     "Mar 2025",        False),
    ]

    x0, y0 = Inches(0.35), Inches(1.45)
    rh = Inches(0.59)
    col_ws = [Inches(4.8), Inches(2.4), Inches(1.5)]

    # header
    for j, (hdr, cw) in enumerate(zip(["Activity", "Timeline", "Status"], col_ws)):
        x = x0 + sum(col_ws[:j])
        rect(sl, x, y0, cw, rh, ACC_BLUE)
        txt(sl, hdr, x + Inches(0.07), y0 + Inches(0.1), cw, rh,
            size=12, bold=True, color=WHITE)

    for i, (phase, timeline, done) in enumerate(phases):
        y = y0 + rh + i * rh
        bg = LGRAY if i % 2 == 0 else WHITE
        status = "✔  Completed" if done else "⬜  Pending"
        s_color = GREEN if done else RED
        for j, (cell, cw) in enumerate(zip([phase, timeline, status], col_ws)):
            x = x0 + sum(col_ws[:j])
            rect(sl, x, y, cw, y0 + rh - y0 if False else rh, bg)
            c = s_color if j == 2 else BLACK
            txt(sl, cell, x + Inches(0.07), y + Inches(0.1), cw - Inches(0.1), rh,
                size=11, color=c, bold=(j == 2))


def s_architecture(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "System Architecture")
    add_footer(sl, num)
    txt(sl, "Fig 2: System Architecture Diagram",
        Inches(0.4), Inches(1.05), Inches(9.2), Inches(0.3),
        size=11, italic=True, color=GRAY)

    steps = [
        ("Camera\nInput", "Video\nCapture"),
        ("Pre-\nprocessing", "Resize &\nNormalize"),
        ("Face\nDetection", "YuNet\nCNN"),
        ("Face\nRecognition", "SFace\nCNN"),
        ("Gait\nDetection", "MOG2"),
        ("Output\n& Log", "GUI +\nCSV"),
    ]
    bw, bh = Inches(1.42), Inches(1.3)
    sx = Inches(0.3)
    sy = Inches(1.5)
    for i, (top, bot) in enumerate(steps):
        x = sx + i * (bw + Inches(0.14))
        rect(sl, x, sy, bw, bh, LGRAY)
        rect(sl, x, sy, bw, Inches(0.06), ACC_BLUE)
        txt(sl, top, x + Inches(0.05), sy + Inches(0.1),
            bw - Inches(0.1), Inches(0.55),
            size=11, bold=True, color=TITLE_BLUE, align=PP_ALIGN.CENTER)
        txt(sl, bot, x + Inches(0.05), sy + Inches(0.65),
            bw - Inches(0.1), Inches(0.55),
            size=10, color=GRAY, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            ax = x + bw + Inches(0.01)
            txt(sl, "→", ax, sy + Inches(0.45), Inches(0.12), Inches(0.4),
                size=14, color=GRAY)

    # description bullets below
    items = [
        "Video is captured frame-by-frame from webcam using cv2.VideoCapture.",
        "Frames are passed to YuNet CNN for face detection and MOG2 for motion detection simultaneously.",
        "Detected faces are matched against stored SFace CNN embeddings via cosine similarity.",
        "Gait is classified as Standing / Walking / Running based on centroid displacement over 30 frames.",
        "Results are overlaid on the live video feed and logged to recognition_log.csv with timestamps.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(3.0), Inches(9.2), Inches(3.8), size=12)


def s_data_workflow(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Data Processing Workflow")
    add_footer(sl, num)
    txt(sl, "Fig 3: Data Processing Pipeline",
        Inches(0.4), Inches(1.05), Inches(9.2), Inches(0.3),
        size=11, italic=True, color=GRAY)

    steps_data = [
        ("Data\nCollection",        "Live camera\nor dataset"),
        ("Pre-\nprocessing",        "Resize, grayscale\nnormalize"),
        ("Feature\nExtraction",     "CNN embeddings\n(SFace / MOG2)"),
        ("Feature\nRepresentation", "128-dim\nvectors"),
        ("Classifier",              "Cosine similarity\nmatching"),
        ("Output",                  "Identity +\nGait label"),
    ]
    bw, bh = Inches(1.42), Inches(1.3)
    sx, sy = Inches(0.3), Inches(1.45)
    for i, (top, bot) in enumerate(steps_data):
        x = sx + i * (bw + Inches(0.14))
        rect(sl, x, sy, bw, bh, LGRAY)
        rect(sl, x, sy, bw, Inches(0.06), ACC_BLUE)
        txt(sl, top, x + Inches(0.05), sy + Inches(0.1),
            bw - Inches(0.1), Inches(0.55),
            size=11, bold=True, color=TITLE_BLUE, align=PP_ALIGN.CENTER)
        txt(sl, bot, x + Inches(0.05), sy + Inches(0.65),
            bw - Inches(0.1), Inches(0.55),
            size=10, color=GRAY, align=PP_ALIGN.CENTER)
        if i < len(steps_data) - 1:
            txt(sl, "→", x + bw, sy + Inches(0.45), Inches(0.14), Inches(0.4),
                size=14, color=GRAY)

    rows = [
        ("Data Collection",       "Captures real-time video input using USB webcam or CCTV camera."),
        ("Pre-processing",        "Frame resized to 112×112; converted to BGR; noise removed."),
        ("Feature Extraction",    "SFace CNN extracts 128-dim embedding; MOG2 extracts motion blob."),
        ("Feature Representation","Face: 128-dim float vector.  Gait: centroid trail over 30 frames."),
        ("Classifier",            "Cosine similarity ≥ 0.363 → known person; below → Unknown."),
        ("Output",                "Bounding boxes + labels drawn on frame; event written to CSV log."),
    ]
    y = Inches(2.9)
    for label, desc in rows:
        txt(sl, label, Inches(0.4), y, Inches(2.8), Inches(0.4),
            size=12, bold=True, color=ACC_BLUE)
        txt(sl, desc,  Inches(3.3), y, Inches(6.3), Inches(0.4),
            size=12, color=BLACK)
        rect(sl, Inches(0.4), y + Inches(0.38), Inches(9.2), Pt(0.5), LGRAY)
        y += Inches(0.55)


def s_face_detection(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Module 1 — Face Detection",
                    "face_module/face_detector.py  ·  YuNet CNN  (cv2.FaceDetectorYN)")
    add_footer(sl, num)
    items = [
        "Algorithm: YuNet — a lightweight CNN trained for multi-scale face detection.",
        "Model: face_detection_yunet_2023mar.onnx (~230 KB), loaded via OpenCV DNN backend.",
        "Input: BGR video frame.   Output: list of (x, y, w, h) bounding boxes + 5 landmarks.",
        "Score threshold = 0.7,  NMS threshold = 0.3,  top-K = 50 detections per frame.",
        "Significantly more robust than Haar Cascade under varying pose and lighting conditions.",
        "Model auto-downloads on first run; falls back to Haar Cascade if offline.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(5.5), Inches(4.0), size=13)

    # Code panel
    rect(sl, Inches(6.1), Inches(1.15), Inches(3.65), Inches(4.5),
         RGBColor(0xF2, 0xF2, 0xF2))
    code = ("# Create YuNet detector\ndet = cv2.FaceDetectorYN\n"
            "  .create(model, \"\",\n"
            "          (width, height),\n"
            "          score_threshold=0.7)\n\n"
            "# Detect faces\n_, faces = det.detect(frame)\n\n"
            "# faces[i, 0:4] = x,y,w,h\n"
            "# faces[i, 4:14]= 5 landmarks\n"
            "# faces[i, 14]  = confidence")
    txt(sl, code, Inches(6.25), Inches(1.3), Inches(3.35), Inches(4.2),
        size=10, italic=True, color=ACC_BLUE)


def s_face_recognition(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Module 2 — Face Recognition",
                    "face_module/face_recognizer.py  ·  SFace CNN  (cv2.FaceRecognizerSF)")
    add_footer(sl, num)
    items = [
        "Algorithm: SFace — CNN trained with sigmoid-constrained hypersphere loss.",
        "Model: face_recognition_sface_2021dec.onnx (~37 MB), loaded via OpenCV DNN.",
        "Each face image is converted to a 128-dimensional embedding vector.",
        "Recognition: cosine similarity between query and stored embeddings.",
        "Threshold: cosine score ≥ 0.363 → recognized; below threshold → 'Unknown'.",
        "Registration: single photo per person; embedding stored instantly — no retraining.",
        "Embeddings stored in models/face_embeddings.pkl; persists across app restarts.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.15), Inches(9.2), Inches(4.5), size=13)

    txt(sl, "Comparison — SFace CNN vs LBPH:",
        Inches(0.4), Inches(5.6), Inches(9.2), Inches(0.38),
        size=13, bold=True, color=TITLE_BLUE)

    cols = ["Metric", "LBPH (classical)", "SFace CNN (this project)"]
    rows_cmp = [
        ("Feature type",      "Hand-crafted LBP histograms",   "Learned CNN embeddings (128-dim)"),
        ("Lighting variation","Sensitive",                      "Robust"),
        ("Registration",      "Requires model retraining",     "Instant embedding storage"),
        ("Accuracy (frontal)","~75–85%",                       "~88–93%"),
    ]
    x0, y0 = Inches(0.35), Inches(5.95)
    rh, cws = Inches(0.38), [Inches(2.3), Inches(3.1), Inches(3.9)]
    for j, (h, cw) in enumerate(zip(cols, cws)):
        x = x0 + sum(cws[:j])
        rect(sl, x, y0, cw, rh, ACC_BLUE)
        txt(sl, h, x + Inches(0.05), y0 + Inches(0.04), cw, rh,
            size=10, bold=True, color=WHITE)
    for i, row in enumerate(rows_cmp):
        bg = LGRAY if i % 2 == 0 else WHITE
        for j, (cell, cw) in enumerate(zip(row, cws)):
            x = x0 + sum(cws[:j])
            y = y0 + rh + i * rh
            rect(sl, x, y, cw, rh, bg)
            txt(sl, cell, x + Inches(0.05), y + Inches(0.03),
                cw - Inches(0.1), rh, size=10, color=BLACK)


def s_gait(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Module 3 — Gait Detection & Analysis",
                    "gait_module/motion_detector.py  ·  gait_module/gait_analyzer.py")
    add_footer(sl, num)

    txt(sl, "Motion Detector — MOG2 Background Subtraction:",
        Inches(0.4), Inches(1.1), Inches(9.2), Inches(0.38),
        size=14, bold=True, color=TITLE_BLUE)
    bullet_box(sl,
        ["cv2.createBackgroundSubtractorMOG2() isolates moving foreground from static background.",
         "Morphological dilation (cv2.dilate) fills gaps and removes small noise blobs.",
         "Contours above minimum area threshold are classified as walking persons.",
         "Each person region → bounding box + centroid returned to Gait Analyzer."],
        Inches(0.4), Inches(1.5), Inches(9.2), Inches(1.8), size=13)

    txt(sl, "Gait Analyzer — Centroid Tracking & Classification:",
        Inches(0.4), Inches(3.35), Inches(9.2), Inches(0.38),
        size=14, bold=True, color=TITLE_BLUE)
    bullet_box(sl,
        ["Each detected person is assigned a track ID; centroid positions stored over 30 frames.",
         "Average pixel displacement per frame = gait speed.",
         "Classification thresholds:   < 3 px/frame → Standing   |   3–15 → Walking   |   > 15 → Running",
         "Gait label + confidence score (%) overlaid as orange bounding box on live video."],
        Inches(0.4), Inches(3.75), Inches(9.2), Inches(2.0), size=13)


def s_gui(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "GUI — Desktop Surveillance Application",
                    "app.py  ·  Python Tkinter")
    add_footer(sl, num)

    rows = [
        ("▶  Start / Stop Camera",  "Launches background AI thread; releases webcam on stop."),
        ("📸  Register My Face",     "Captures frame → detects face → stores SFace CNN embedding."),
        ("💾  Screenshot",           "Saves annotated frame as PNG with date-time filename."),
        ("🔄  Reload Face DB",       "Hot-reloads embeddings without restarting the application."),
        ("🗑  Clear Log",            "Clears the on-screen recognition event list."),
        ("FPS Counter",             "Live frames-per-second shown in the control panel."),
        ("Recognition Log Panel",  "Scrollable list: time  ·  name  ·  gait label (color-coded)."),
    ]
    y = Inches(1.15)
    for btn, desc in rows:
        txt(sl, btn,  Inches(0.4), y, Inches(2.9), Inches(0.42),
            size=12, bold=True, color=ACC_BLUE)
        txt(sl, desc, Inches(3.4), y, Inches(6.25), Inches(0.42),
            size=12, color=BLACK)
        rect(sl, Inches(0.4), y + Inches(0.4), Inches(9.2), Pt(0.8), LGRAY)
        y += Inches(0.62)


def s_progress_summary(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Progress Till Date — Progress Summary")
    add_footer(sl, num)

    sections = [
        ("Face Detection (Completed)",
         "Implemented YuNet CNN detector via OpenCV DNN. "
         "Auto-downloads ONNX model; falls back to Haar if offline."),
        ("Face Recognition (Completed)",
         "Replaced LBPH with SFace CNN. Embedding-based recognition; "
         "cosine similarity matching; instant one-shot registration."),
        ("Gait Detection & Analysis (Completed)",
         "MOG2 background subtraction for person detection; "
         "centroid tracking over 30 frames; Standing/Walking/Running classification."),
        ("GUI Application (Completed)",
         "Full Tkinter desktop app: live video feed, face + gait overlay, "
         "register, screenshot, reload DB, recognition log panel."),
        ("Accuracy Testing Script (Completed)",
         "measure_accuracy.py implements LOOCV, augmentation robustness test, "
         "and Unknown rejection rate evaluation."),
        ("Windows Launcher (Completed)",
         "run.bat auto-installs requirements and launches the app on Windows."),
    ]
    y = Inches(1.15)
    for title, desc in sections:
        rect(sl, Inches(0.35), y, Inches(0.38), Inches(0.75), GREEN)
        txt(sl, "✔", Inches(0.35), y + Inches(0.1), Inches(0.38), Inches(0.5),
            size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, title, Inches(0.85), y + Inches(0.02), Inches(8.8), Inches(0.35),
            size=12, bold=True, color=TITLE_BLUE)
        txt(sl, desc, Inches(0.85), y + Inches(0.37), Inches(8.8), Inches(0.35),
            size=11, color=BLACK)
        y += Inches(0.88)


def s_results(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Result and Discussion")
    add_footer(sl, num)

    txt(sl, "Evaluation Setup:",
        Inches(0.4), Inches(1.1), Inches(9.2), Inches(0.35),
        size=13, bold=True, color=TITLE_BLUE)
    bullet_box(sl, [
        "Input: live video frames from USB webcam at 720p resolution.",
        "Processing: YuNet face detection + SFace recognition + MOG2 gait extraction.",
        "Evaluation script: measure_accuracy.py (LOOCV + augmentation + rejection tests).",
    ], Inches(0.4), Inches(1.45), Inches(9.2), Inches(1.3), size=12)

    metrics = [
        ("Face Recognition Accuracy",  "~88–93%",  "Frontal faces; degrades with extreme pose."),
        ("Gait Classification Rate",   "~90%",     "Single-person; clear background required."),
        ("Processing Speed",           "15–25 FPS","Intel i5 CPU, 8 GB RAM — no GPU needed."),
        ("Registration Time",          "< 2 sec",  "Instant embedding; no model retraining."),
        ("Unknown Rejection Rate",     "~95%",     "Cosine threshold = 0.363 reliably rejects strangers."),
    ]
    txt(sl, "Evaluation Metrics:", Inches(0.4), Inches(2.85), Inches(9.2), Inches(0.35),
        size=13, bold=True, color=TITLE_BLUE)

    for i, (metric, val, note) in enumerate(metrics):
        y = Inches(3.25) + i * Inches(0.73)
        rect(sl, Inches(0.35), y, Inches(9.2), Inches(0.68), LGRAY if i % 2 == 0 else WHITE)
        txt(sl, metric, Inches(0.5), y + Inches(0.1), Inches(3.5), Inches(0.45),
            size=12, bold=True, color=TITLE_BLUE)
        txt(sl, val, Inches(4.1), y + Inches(0.1), Inches(1.4), Inches(0.45),
            size=14, bold=True, color=ACC_BLUE, align=PP_ALIGN.CENTER)
        txt(sl, note, Inches(5.6), y + Inches(0.1), Inches(3.7), Inches(0.45),
            size=11, italic=True, color=GRAY)


def s_conclusion(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "Conclusion")
    add_footer(sl, num)
    txt(sl,
        "A deep learning–based real-time surveillance system combining face and gait recognition "
        "has been successfully implemented and tested.",
        Inches(0.4), Inches(1.1), Inches(9.2), Inches(0.7), size=14, color=BLACK)
    items = [
        "CNN-based recognition (YuNet + SFace) achieves 88–93% accuracy, outperforming classical LBPH.",
        "Gait detection using MOG2 correctly classifies standing, walking, and running at ~90% rate.",
        "One-shot face registration makes the system practical without large datasets.",
        "Full desktop GUI enables operator control: start/stop, register, screenshot, log.",
        "Runs at 15–25 FPS on standard laptop CPU — no GPU or cloud services required.",
        "Modular design (face_module, gait_module, utils) supports independent testing and future upgrades.",
        "Provides a foundation for multi-camera deployment, biometric score fusion, and edge computing.",
    ]
    bullet_box(sl, items, Inches(0.4), Inches(1.85), Inches(9.2), Inches(4.5), size=13)


def s_references(prs, num):
    sl = blank(prs)
    slide_title_bar(sl, "References & Bibliography")
    add_footer(sl, num)
    refs = [
        "Pundir, A., & Sharma, M. (2023). A Review of Deep Learning Approaches for Human Gait Recognition. INOCON 2023, IEEE.",
        "Sepas-Moghaddam, A., & Etemad, A. (2022). Deep Gait Recognition: A Survey. IEEE TPAMI, 45(1), 264–284.",
        "Sheng, Y. et al. (2021). YuNet: A Tiny Millisecond-level Face Detector. IEEE TBIOM.",
        "Wang, F. et al. (2021). SFace: Sigmoid-Constrained Hypersphere Loss for Face Recognition. IEEE TIP.",
        "Lal, A., & Nithyakani, P. (2023). Gait Speed-Based Recognition using Deep 2-D CNN. ICCCI 2023, IEEE.",
        "Viola, P., & Jones, M. (2001). Rapid Object Detection using a Boosted Cascade of Simple Features. CVPR.",
        "OpenCV Documentation — https://docs.opencv.org/  |  opencv/opencv_zoo (YuNet & SFace ONNX models).",
    ]
    y = Inches(1.15)
    for ref in refs:
        txt(sl, ref, Inches(0.4), y, Inches(9.2), Inches(0.52), size=12, color=BLACK)
        y += Inches(0.67)


def s_end(prs, num):
    sl = blank(prs)
    rect(sl, 0, 0, SLIDE_W, Inches(0.08), ACC_BLUE)
    rect(sl, 0, Inches(7.42), SLIDE_W, Inches(0.08), ACC_BLUE)
    txt(sl, "Thank You",
        Inches(0.6), Inches(2.8), Inches(8.8), Inches(1.0),
        size=40, bold=True, color=TITLE_BLUE, align=PP_ALIGN.CENTER)
    txt(sl, "Questions & Discussion",
        Inches(0.6), Inches(3.9), Inches(8.8), Inches(0.5),
        size=18, color=GRAY, align=PP_ALIGN.CENTER)
    txt(sl, FOOTER_TEXT,
        Inches(0.6), Inches(5.2), Inches(8.8), Inches(0.35),
        size=11, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
    txt(sl, str(num),
        Inches(9.4), Inches(7.12), Inches(0.5), Inches(0.35),
        size=10, bold=True, color=GRAY, align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════
# ASSEMBLE
# ══════════════════════════════════════════════════════════════

def main():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    builders = [
        s_title, s_contents, s_introduction, s_overview,
        s_objectives_primary, s_objectives_secondary, s_feasibility,
        s_literature, s_problem_definition, s_proposed_solution,
        s_requirements, s_team, s_gantt, s_architecture,
        s_data_workflow, s_face_detection, s_face_recognition,
        s_gait, s_gui, s_progress_summary,
        s_results, s_conclusion, s_references, s_end,
    ]

    for n, builder in enumerate(builders, 1):
        builder(prs, n)

    out = "/home/user/FACEE/FACEE_Presentation.pptx"
    prs.save(out)
    print(f"Done — {len(prs.slides)} slides → {out}")


if __name__ == "__main__":
    main()
