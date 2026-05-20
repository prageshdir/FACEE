"""Generate gantt_chart.png matching the project Gantt chart image."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

RED   = '#FF0000'
GREEN = '#00B050'
WHITE = '#FFFFFF'
BLACK = '#000000'

# ── Geometry ──────────────────────────────────────────────────
COL_W = [2.2] + [1.3] * 6          # Activities col + 6 period cols
COL_X = [0.0]
for w in COL_W:
    COL_X.append(COL_X[-1] + w)    # 0,2.2,3.5,4.8,6.1,7.4,8.7,10.0

HDR_H = 0.72
ROW_H = 0.47
ROW_Y = [0.0, HDR_H]
for _ in range(14):                 # 7 activities × 2 sub-rows
    ROW_Y.append(ROW_Y[-1] + ROW_H)

TW, TH = COL_X[-1], ROW_Y[-1]

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, TW); ax.set_ylim(0, TH)
ax.invert_yaxis(); ax.axis('off')
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)


# ── Helpers ────────────────────────────────────────────────────
def rect(x, y, w, h, color, z=1):
    ax.add_patch(mpatches.Rectangle(
        (x, y), w, h, facecolor=color, edgecolor='none', zorder=z))


def fill_cell(col, row, color, fs=0.0, fe=1.0):
    """Fill (part of) a cell. fs/fe = start/end fractions 0-1."""
    cw = COL_X[col+1] - COL_X[col]
    rect(COL_X[col] + fs*cw, ROW_Y[row], (fe-fs)*cw,
         ROW_Y[row+1] - ROW_Y[row], color)


def ar(ai, sub):
    """Data row index: activity ai (0-6), sub-row 0=planned/red 1=actual/green."""
    return 1 + ai * 2 + sub


# ── White background ───────────────────────────────────────────
rect(0, 0, TW, TH, WHITE)

# ── Gantt colour fills ─────────────────────────────────────────
R, G = RED, GREEN

# 0 — Feasibility Study
fill_cell(1, ar(0,0), R);  fill_cell(2, ar(0,0), R)
fill_cell(1, ar(0,1), G);  fill_cell(2, ar(0,1), G)

# 1 — Literature Survey
fill_cell(1, ar(1,0), R);  fill_cell(2, ar(1,0), R)
fill_cell(4, ar(1,0), R);  fill_cell(5, ar(1,0), R)
fill_cell(1, ar(1,1), G);  fill_cell(2, ar(1,1), G)

# 2 — Interface Design   (partial red in col3; partial green in col2)
fill_cell(2, ar(2,0), R);  fill_cell(3, ar(2,0), R, fe=0.60)
fill_cell(2, ar(2,1), G,   fe=0.65)

# 3 — Database Development  (partial start in col2; partial green in col3)
fill_cell(2, ar(3,0), R, fs=0.55)
fill_cell(3, ar(3,0), R);  fill_cell(4, ar(3,0), R); fill_cell(5, ar(3,0), R)
fill_cell(2, ar(3,1), G, fs=0.55)
fill_cell(3, ar(3,1), G, fe=0.28)

# 4 — Module Integration
fill_cell(4, ar(4,0), R);  fill_cell(5, ar(4,0), R)

# 5 — Testing and Deployment  (partial col6)
fill_cell(5, ar(5,0), R);  fill_cell(6, ar(5,0), R, fe=0.38)

# 6 — Documentation
fill_cell(1, ar(6,0), R);  fill_cell(2, ar(6,0), R)
fill_cell(4, ar(6,0), R);  fill_cell(5, ar(6,0), R); fill_cell(6, ar(6,0), R)
fill_cell(1, ar(6,1), G);  fill_cell(2, ar(6,1), G)

# ── Grid lines ─────────────────────────────────────────────────
LW = 1.8
for cx in COL_X:
    ax.plot([cx, cx], [0, TH], '-', color=BLACK, lw=LW, zorder=2)
for ry in ROW_Y:
    ax.plot([0, TW], [ry, ry], '-', color=BLACK, lw=LW, zorder=2)

# ── Text ───────────────────────────────────────────────────────
HDRS = ["Activities",
        "28 Jan-\n7 Feb", "8 Feb-\n19 Mar", "20 Mar-\n2 May",
        "3 May-\n6 Jun",  "7 Jun-\n4 July",  "5 Jul-10\nJul"]

for ci, h in enumerate(HDRS):
    cw = COL_X[ci+1] - COL_X[ci]
    rh = ROW_Y[1] - ROW_Y[0]
    xp = COL_X[ci] + (0.15 if ci == 0 else cw/2)
    ha = 'left' if ci == 0 else 'center'
    ax.text(xp, HDR_H/2, h, ha=ha, va='center',
            fontsize=10, fontweight='bold', color=BLACK,
            linespacing=1.25, zorder=3)

ACTS = ["Feasibility\nStudy", "Literature\nSurvey", "Interface\nDesign",
        "Database\nDevelopment", "Module\nIntegration",
        "Testing and\nDeployment", "Documentation"]

for ai, act in enumerate(ACTS):
    tr, br   = ar(ai, 0), ar(ai, 1)
    y_top    = ROW_Y[tr]
    y_bot    = ROW_Y[br + 1]
    ax.text(COL_X[0] + 0.15, (y_top + y_bot) / 2, act,
            ha='left', va='center',
            fontsize=10.5, fontweight='bold', color=BLACK,
            linespacing=1.3, zorder=3)

plt.tight_layout(pad=0.0)
out = '/home/user/FACEE/gantt_chart.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor=WHITE, edgecolor='none')
plt.close()
print(f"Saved → {out}")
