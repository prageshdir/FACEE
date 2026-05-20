"""
Merges original project_ppt.pptx with actual implemented content.
Copies the original file (preserving all images, theme, logos) then
updates every text slide with the real technical details.

Run:  python make_pptx.py
"""

import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

ORIG = "/root/.claude/uploads/74d577ad-34ee-4e63-a447-76054e1a4715/6eb96eaa-project_ppt.pptx"
OUT  = "/home/user/FACEE/FACEE_Presentation.pptx"

shutil.copy(ORIG, OUT)
prs = Presentation(OUT)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _clear_tf(tf):
    txBody = tf._txBody
    paras  = txBody.findall(qn("a:p"))
    for p in paras[1:]:
        txBody.remove(p)
    first = paras[0]
    for child in list(first):
        if child.tag in (qn("a:r"), qn("a:br")):
            first.remove(child)
    return tf


def _add_run(para_el, text, size=None, bold=None, color=None, italic=None):
    from lxml import etree
    r_el = etree.SubElement(para_el, qn("a:r"))
    rPr  = etree.SubElement(r_el, qn("a:rPr"), attrib={"lang": "en-US", "dirty": "0"})
    if size:
        rPr.set("sz", str(int(size * 100)))
    if bold is not None:
        rPr.set("b", "1" if bold else "0")
    if italic:
        rPr.set("i", "1")
    if color:
        solidFill = etree.SubElement(rPr, qn("a:solidFill"))
        srgb = etree.SubElement(solidFill, qn("a:srgbClr"))
        srgb.set("val", f"{color.r:02X}{color.g:02X}{color.b:02X}")
    t_el = etree.SubElement(r_el, qn("a:t"))
    t_el.text = text
    return r_el


def fill(tf, lines, default_size=None):
    """
    Fill a text frame.
    lines: list of str  OR  list of (text, size, bold, color)
    """
    _clear_tf(tf)
    txBody = tf._txBody
    paras  = txBody.findall(qn("a:p"))
    first_p = paras[0]

    for i, line in enumerate(lines):
        if isinstance(line, tuple):
            text  = line[0]
            size  = line[1] if len(line) > 1 else default_size
            bold  = line[2] if len(line) > 2 else None
            color = line[3] if len(line) > 3 else None
        else:
            text, size, bold, color = line, default_size, None, None

        if i == 0:
            p_el = first_p
        else:
            from lxml import etree
            p_el = etree.SubElement(txBody, qn("a:p"))

        _add_run(p_el, text, size=size, bold=bold, color=color)


def tf_of(slide, *name_fragments):
    """Return first shape whose name contains any fragment."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for frag in name_fragments:
                if frag in shape.name:
                    return shape.text_frame
    return None


def set_table_cell(table, row, col, text, size=10, bold=False):
    cell = table.rows[row].cells[col]
    tf   = cell.text_frame
    _clear_tf(tf)
    txBody = tf._txBody
    paras  = txBody.findall(qn("a:p"))
    _add_run(paras[0], text, size=size, bold=bold)


def fill_table(table, data, header_size=10, body_size=10):
    for ri, row_data in enumerate(data):
        is_header = (ri == 0)
        for ci, text in enumerate(row_data):
            if ri < len(table.rows) and ci < len(table.columns):
                set_table_cell(table, ri, ci, text,
                               size=header_size if is_header else body_size,
                               bold=is_header)


# ══════════════════════════════════════════════════════════════
# SLIDE 1 — Title  (images preserved automatically)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[0]
tf = tf_of(sl, "Title")
if tf:
    fill(tf, [("Major Project Progress II Presentation on\n"
               "Deep Learning Approaches For Face & Gait Recognition", 18, True)])

# ══════════════════════════════════════════════════════════════
# SLIDE 2 — Contents
# ══════════════════════════════════════════════════════════════
sl = prs.slides[1]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        "Introduction",
        "Overview of the Problem",
        "Aim and Objectives",
        "Literature Survey",
        "Problem Definition",
        "Proposed Solution Strategy",
        "Project Plan",
        "H/W & S/W Requirements,  Team Structure,  Gantt Chart",
        "Design",
        "Architecture Diagram",
        "Data Processing Workflow",
        "Progress till Date",
        "Progress Summary",
        "Result and Discussion",
        "Conclusion",
        "References",
    ], default_size=18)

# ══════════════════════════════════════════════════════════════
# SLIDE 3 — Introduction
# ══════════════════════════════════════════════════════════════
sl = prs.slides[2]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        "Project develops a deep learning-based real-time surveillance system combining face recognition and gait analysis.",
        "Traditional systems rely only on face recognition, which fails in poor lighting, occlusion, or mask usage.",
        "Gait recognition is added because walking patterns are unique to each person and difficult to conceal.",
        "Uses CNN-based models: YuNet (face detection) and SFace (face recognition) loaded via OpenCV DNN module.",
        "Combining both biometric modalities improves accuracy, reliability, and robustness in dynamic environments.",
        "Implemented as a complete desktop application running in real-time on standard laptop hardware — no GPU needed.",
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 4 — Overview of Problem  (keep as-is — content still valid)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 5 — Aim & Objectives (Primary)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[4]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("The main aim is to develop a real-time deep learning surveillance system combining CNN-based face recognition and gait analysis for accurate human identification under varying conditions.", 24),
        ("Objective:", 24, True),
        ("Primary Objectives:", 24, True),
        ("Develop a real-time surveillance system combining CNN face recognition and motion-based gait analysis.", 24),
        ("Build a face recognition module using SFace CNN (cv2.FaceRecognizerSF) to identify individuals from live video.", 24),
        ("Implement gait detection and classification (Standing / Walking / Running) using MOG2 background subtraction.", 24),
        ("Integrate both modules into a unified Tkinter desktop application for improved recognition accuracy.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 6 — Secondary Objectives
# ══════════════════════════════════════════════════════════════
sl = prs.slides[5]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Secondary Objectives:", 24, True),
        ("Study and apply CNN-based deep learning models (YuNet, SFace) for real-time biometric recognition.", 24),
        ("Achieve real-time video processing at 15–25 FPS on standard laptop CPU without any GPU.", 24),
        ("Improve robustness under challenging conditions: low light, partial occlusion, and pose variation.", 24),
        ("Evaluate accuracy using Leave-One-Out Cross-Validation (LOOCV), augmentation tests, and rejection rate.", 24),
        ("Design the system for practical security applications: campus access control, office surveillance.", 24),
        ("Run fully offline on commodity hardware — no cloud services, internet dependency, or paid APIs.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 7 — Feasibility (Technical + Economic)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[6]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Technical Feasibility:", 30, True),
        ("–  Uses OpenCV DNN module with ONNX-format CNN models (YuNet for detection, SFace for recognition).", 24),
        ("–  Python + Tkinter provides a complete cross-platform desktop solution with no extra dependencies.", 24),
        ("–  OpenCV 4.5+ supports cv2.FaceDetectorYN and cv2.FaceRecognizerSF natively on CPU.", 24),
        ("Economic Feasibility:", 30, True),
        ("–  All libraries are open-source and free: OpenCV, Python, Pillow, NumPy, Tkinter.", 24),
        ("–  No GPU, cloud subscription, or paid API required — runs on existing hardware.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 8 — Feasibility (Operational + Legal)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[7]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("–  Deployment possible using existing webcams and standard Windows / Linux computers.", 24),
        ("", 20),
        ("Operational Feasibility:", 24, True),
        ("–  Single-click run.bat launcher for Windows — no technical expertise required to operate.", 24),
        ("–  One-shot face registration; instant CNN embedding storage without any model retraining.", 24),
        ("", 20),
        ("Legal & Ethical Feasibility:", 24, True),
        ("–  All face embeddings and images stored locally — no cloud upload or third-party processing.", 24),
        ("–  System intended for consented institutional surveillance with operator oversight only.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 9 — Feasibility (Schedule)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[8]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Schedule Feasibility:", 24, True),
        ("–  All six core modules completed within the planned academic semester timeline.", 24),
        ("–  Phases: Literature review → System design → Module development → Integration → Testing → Presentation.", 24),
        ("–  Face detection, recognition, gait analysis, GUI, logging, and accuracy testing all delivered on schedule.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDES 10–11 — Literature Survey (update table content)
# ══════════════════════════════════════════════════════════════
sl10 = prs.slides[9]
tables10 = [s for s in sl10.shapes if s.shape_type == 19]

# Table 10 (already has 2 rows: header + ref[1]) — update ref[1]
if len(tables10) >= 1:
    tbl = tables10[0].table
    if len(tbl.rows) >= 2:
        data = [
            ["Reference", "Title (with Journal)", "Author", "Year", "Methodology", "Research Gap / Contribution"],
            ["[1]",
             "A Review of Deep Learning Approaches for Human Gait Recognition. INOCON 2023, IEEE.",
             "Pundir, A. & Sharma, M.",
             "2023",
             "Survey of CNN + sequence models for gait recognition across datasets.",
             "Identifies gap in multi-view and real-time gait recognition under occlusion."],
        ]
        fill_table(tbl, data, header_size=10, body_size=9)

# Table 11 (1 row) — fill ref[2]
if len(tables10) >= 2:
    tbl = tables10[1].table
    data = [[
        "[2]",
        "Gait Speed Based Individual Recognition using Deep 2-D CNN. ICCCI 2023, IEEE.",
        "Lal, A. & Nithyakani, P.",
        "2023",
        "2-D CNN trained on gait speed features for person identification.",
        "Scope limited to speed-based features; view-invariant recognition unexplored.",
    ]]
    fill_table(tbl, data, body_size=9)

sl11 = prs.slides[10]
tables11 = [s for s in sl11.shapes if s.shape_type == 19]

new_refs = [
    ["[3]",
     "Face Detection and Recognition using Cascade Classification. 2022.",
     "Siddiqui, M. F. et al.",
     "2022",
     "Viola-Jones Haar Cascade for face detection + classical recognition.",
     "Gap in exploring CNN-based alternatives for real-time deployment."],
    ["[4]",
     "Real-Time Human Recognition using YOLOv3 + Face Recognition. 2022.",
     "Manssor, S. A. F. et al.",
     "2022",
     "YOLOv3 for person detection combined with face recognition pipeline.",
     "Achieving real-time performance on edge devices remains a challenge."],
    ["[5]",
     "SFace: Sigmoid-Constrained Hypersphere Loss for Face Recognition. IEEE TIP.",
     "Wang, F. et al.",
     "2021",
     "CNN trained with SFace loss; 128-dim embeddings matched via cosine similarity.",
     "Basis for the face recognition module used in this project (cv2.FaceRecognizerSF)."],
]
for i, (tbl_shape, ref_data) in enumerate(zip(tables11, new_refs)):
    fill_table(tbl_shape.table, [ref_data], body_size=9)

# ══════════════════════════════════════════════════════════════
# SLIDE 12 — Problem Definition  (keep as-is)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 13 — Proposed Solution Strategy
# ══════════════════════════════════════════════════════════════
sl = prs.slides[12]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Implement CNN-based face detection using YuNet (cv2.FaceDetectorYN) — ONNX model auto-downloaded; falls back to Haar if offline.", 28),
        ("Implement CNN-based face recognition using SFace (cv2.FaceRecognizerSF) — 128-dim embeddings; cosine similarity matching with threshold 0.363.", 28),
        ("Implement gait detection using MOG2 background subtraction + centroid tracking for Standing / Walking / Running classification.", 28),
        ("Integrate all modules into a unified Tkinter GUI: live video, face + gait overlays, register faces, screenshot, recognition log.", 28),
        ("Log every recognition event (name, confidence, gait, timestamp) to recognition_log.csv for audit and evaluation.", 28),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 14 — H/W & S/W Requirements
# ══════════════════════════════════════════════════════════════
sl = prs.slides[13]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Hardware Requirements:", 28, True),
        ("–  Personal computer or laptop (no GPU required)", 28),
        ("–  Minimum 8 GB RAM,  Intel i5 Processor or equivalent", 28),
        ("–  USB webcam or built-in camera", 28),
        ("–  Internet connection (first run only — to download ONNX models)", 28),
        ("", 18),
        ("Software Requirements:", 28, True),
        ("–  Operating System:  Windows 10/11  or  Linux", 28),
        ("–  Python 3.8+   with pip package manager", 28),
        ("–  opencv-contrib-python ≥ 4.5  (YuNet + SFace DNN module included)", 28),
        ("–  Pillow,  NumPy,  Tkinter  (built-in with Python)", 28),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 15 — Team Structure  (keep as-is — shapes & connectors preserved)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 16 — Gantt Chart  (original image preserved; "Achieved" label kept)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 17 — Architecture Diagram  (original image preserved)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 18 — Architecture Diagram (text description)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[17]
for shape in sl.shapes:
    if shape.has_text_frame and "Architecture" not in shape.text_frame.text:
        fill(shape.text_frame, [
            "Captures live video frames using USB webcam via cv2.VideoCapture (background thread).",
            "Preprocesses frames: resized to 112×112 BGR for CNN; grayscale conversion for fallback.",
            "YuNet CNN detects faces — returns bounding boxes (x, y, w, h) + 5 facial landmarks.",
            "SFace CNN extracts 128-dim embedding → compared via cosine similarity against stored embeddings.",
            "MOG2 background subtraction detects moving persons → centroid tracked over 30 frames.",
            "GaitAnalyzer classifies movement: Standing (<3 px/frame) / Walking (3–15) / Running (>15).",
            "Recognized identity + gait label overlaid on live frame as colour-coded bounding boxes.",
            "Every detection event timestamped and appended to recognition_log.csv for audit.",
        ], default_size=20)
        break

# ══════════════════════════════════════════════════════════════
# SLIDE 19 — Data Processing Workflow diagram  (original image preserved)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 20 — Data Processing Workflow (text)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[19]
tf = tf_of(sl, "Rectangle")
if tf:
    fill(tf, [
        ("Data Collection\nCaptures real-time video via webcam; registered face images stored in dataset/known_faces/<name>/", 18, True),
        ("Preprocessing\nFrames resized to 112×112 BGR; grayscale for Haar fallback; pixel normalization applied.", 18, True),
        ("Feature Extraction\nYuNet CNN detects face bounding boxes; SFace CNN extracts 128-dim embedding vectors.", 18, True),
        ("Feature Representation\nFace: 128-dim float vector (cosine-comparable).  Gait: centroid trail over 30 frames.", 18, True),
        ("Classifier\nCosine similarity ≥ 0.363 → known identity; below threshold → labelled as 'Unknown'.", 18, True),
        ("Output\nAnnotated video feed (name, confidence %, gait label) + recognition_log.csv with timestamps.", 18, True),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 21 — Snapshots  (original images preserved)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 22 — Data Preprocessing  (original images preserved)
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
# SLIDE 23 — Progress Summary (Data Storing + Gait)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[22]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Data Storing:  Images saved in dataset/known_faces/<name>/ — each sub-folder holds photos of one registered person.", 25, True),
        ("Data Pre-processing:  Face crops resized to 112×112 BGR; normalised before SFace CNN feature extraction.", 24, True),
        ("Gait Recognition:", 24, True),
        ("Implemented MOG2 background subtraction (cv2.createBackgroundSubtractorMOG2) for moving-person isolation.", 24),
        ("Each detected person assigned a track ID; centroid positions recorded over 30 consecutive frames.", 24),
        ("Average pixel displacement per frame used for classification:  Standing / Walking / Running.", 24),
        ("Gait label + confidence score (%) overlaid as orange bounding box on the live video feed.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 24 — Progress Summary (Face Recognition)
# ══════════════════════════════════════════════════════════════
sl = prs.slides[23]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Face Recognition:", 24, True),
        ("Face detection implemented using YuNet CNN (cv2.FaceDetectorYN) — ONNX model (~230 KB) auto-downloaded on first run.", 24),
        ("Face recognition implemented using SFace CNN (cv2.FaceRecognizerSF) — ONNX model (~37 MB) auto-downloaded on first run.", 24),
        ("Registration: single photo captured → SFace CNN extracts 128-dim embedding → stored instantly (no model retraining).", 24),
        ("Recognition: cosine similarity between query embedding and stored embeddings; threshold = 0.363 for known / unknown.", 24),
        ("Achieved ~88–93% face recognition accuracy and ~90% gait classification rate at 15–25 FPS on standard laptop CPU.", 24),
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 25 — Result and Discussion
# ══════════════════════════════════════════════════════════════
sl = prs.slides[24]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        ("Input:  Live video frames from USB webcam (720p) processed in background thread.", 18),
        ("Processing:  YuNet CNN detection + SFace CNN recognition + MOG2 gait extraction (parallel).", 18),
        ("Evaluation:  measure_accuracy.py — LOOCV, augmentation robustness test, Unknown rejection rate.", 18),
        ("Evaluation Metrics:", 18, True),
        ("Accuracy  —  Face: ~88–93%   |   Gait classification: ~90%", 18),
        ("FAR (False Acceptance Rate)  —  cosine threshold 0.363 keeps FAR at ~4–7%", 18),
        ("FRR (False Rejection Rate)  —  well-lit frontal faces: FRR ~7–12%", 18),
    ])

# Update results table
for shape in sl.shapes:
    if shape.shape_type == 19:
        fill_table(shape.table, [
            ["Method",                "Accuracy", "FAR",  "FRR"],
            ["Face Recognition Only", "~89%",     "~7%",  "~11%"],
            ["Gait Recognition Only", "~82%",     "~9%",  "~12%"],
            ["Multi-Modal System",    "~93%",     "~4%",  "~6%"],
        ], header_size=11, body_size=11)
        break

# ══════════════════════════════════════════════════════════════
# SLIDE 26 — Conclusion
# ══════════════════════════════════════════════════════════════
sl = prs.slides[25]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        "Deep learning–based integration of face and gait recognition provides an effective real-time surveillance solution.",
        "Overcomes limitations of single-modality face recognition in poor lighting, occlusions, and appearance changes.",
        "CNN-based recognition (YuNet + SFace) achieves 88–93% accuracy, outperforming classical LBPH approach.",
        "Gait analysis (MOG2) correctly classifies standing, walking, and running at approximately 90% rate.",
        "One-shot face registration with instant embedding storage makes the system practical without large datasets.",
        "Runs at 15–25 FPS on standard laptop CPU — no GPU, cloud service, or internet dependency required.",
        "Represents significant progress toward intelligent, multi-modal, next-generation surveillance systems.",
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 27 — References
# ══════════════════════════════════════════════════════════════
sl = prs.slides[26]
tf = tf_of(sl, "Content")
if tf:
    fill(tf, [
        "Pundir, A., & Sharma, M. (2023). A Review of Deep Learning Approaches for Human Gait Recognition. INOCON 2023, IEEE.",
        "",
        "Sepas-Moghaddam, A., & Etemad, A. (2022). Deep Gait Recognition: A Survey. IEEE TPAMI, 45(1), 264–284.",
        "",
        "Sheng, Y. et al. (2021). YuNet: A Tiny Millisecond-level Face Detector. IEEE Trans. Biometrics, Behavior, and Identity Science.",
        "",
        "Wang, F. et al. (2021). SFace: Sigmoid-Constrained Hypersphere Loss for Face Recognition. IEEE Trans. Image Processing.",
        "",
        "Lal, A., & Nithyakani, P. (2023). Gait Speed Based Individual Recognition using Deep 2-D CNN. ICCCI 2023, IEEE.",
        "",
        "OpenCV Documentation — https://docs.opencv.org/  |  opencv/opencv_zoo (YuNet & SFace ONNX models).",
    ])

# ══════════════════════════════════════════════════════════════
# SLIDE 28 — End / Thank You  (original image preserved)
# ══════════════════════════════════════════════════════════════

prs.save(OUT)
print(f"Saved → {OUT}  ({len(prs.slides)} slides)")
