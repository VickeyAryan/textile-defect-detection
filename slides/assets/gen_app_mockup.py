"""Recreate the real Streamlit app result (the actual prediction the user got)
as a clean mockup image for the slide deck."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUT_DIR = os.path.dirname(__file__)

BLUE = "#2a78d6"
MUTED = "#898781"
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e1e0d9"

probs = [
    ("hole", 0.604),
    ("horizontal", 0.269),
    ("Vertical", 0.123),
    ("stain", 0.001),
    ("defect free", 0.001),
    ("lines", 0.001),
    ("Pinched fabric", 0.0),
    ("Needle mark", 0.0),
    ("Broken stitch", 0.0),
]

fig, ax = plt.subplots(figsize=(8, 6), facecolor=SURFACE)
fig.patch.set_facecolor(SURFACE)

# window chrome
ax.add_patch(patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.01,rounding_size=0.02",
                                     linewidth=1.5, edgecolor=MUTED, facecolor="white",
                                     transform=ax.transAxes))

ax.text(0.06, 0.92, "Fabric Defect Detector", fontsize=18, fontweight="bold",
        color=TEXT_PRIMARY, transform=ax.transAxes)
ax.text(0.06, 0.86, "Upload a fabric image to classify it as defect-free or a specific defect type.",
        fontsize=10.5, color=TEXT_SECONDARY, transform=ax.transAxes)

ax.text(0.06, 0.76, "Prediction: hole", fontsize=15, fontweight="bold", color=TEXT_PRIMARY,
        transform=ax.transAxes)
ax.text(0.06, 0.71, "Confidence: 60.4%", fontsize=12, color=TEXT_SECONDARY, transform=ax.transAxes)

ax.text(0.06, 0.64, "Class probabilities:", fontsize=11, color=TEXT_SECONDARY, transform=ax.transAxes)

bar_top = 0.58
bar_h = 0.045
gap = 0.058
for i, (name, p) in enumerate(probs):
    y = bar_top - i * gap
    ax.add_patch(patches.Rectangle((0.06, y - bar_h / 2), 0.6, bar_h, facecolor=GRID,
                                    transform=ax.transAxes))
    ax.add_patch(patches.Rectangle((0.06, y - bar_h / 2), 0.6 * p, bar_h, facecolor=BLUE,
                                    transform=ax.transAxes))
    ax.text(0.68, y, f"{name}: {p:.1%}", fontsize=10.5, va="center", color=TEXT_PRIMARY,
            transform=ax.transAxes)

ax.axis("off")
fig.savefig(os.path.join(OUT_DIR, "app_mockup.png"), dpi=200, facecolor=SURFACE)
print("Saved app_mockup.png")
