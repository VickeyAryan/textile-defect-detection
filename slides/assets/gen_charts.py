"""Generate the remaining data-driven chart assets for the slide deck:
pixel-grid illustration, RGB channel split, convolution illustration,
train/val/test split, real training curves, and an annotated confusion
matrix explaining precision (columns) vs recall (rows)."""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

OUT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(OUT_DIR, "..", "..")

# --- validated palette ---
BLUE = "#2a78d6"
AQUA = "#1baf7a"
YELLOW = "#eda100"
VIOLET = "#4a3aa7"
RED = "#e34948"
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["text.color"] = TEXT_PRIMARY
plt.rcParams["axes.edgecolor"] = MUTED

SAMPLE_IMAGE = r"C:\Users\chirl\.cache\kagglehub\datasets\ziya07\multi-class-fabric-defect-detection-dataset\versions\3\Dataset\hole\1.jpg"


# ---------------------------------------------------------------------------
# 1. Pixel grid: a tiny patch of a real image shown as an image + as numbers
# ---------------------------------------------------------------------------
def gen_pixel_grid():
    img = Image.open(SAMPLE_IMAGE).convert("L").resize((224, 224))
    arr = np.array(img)
    patch = arr[80:88, 80:88]  # 8x8 patch

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), facecolor=SURFACE)

    axes[0].imshow(Image.open(SAMPLE_IMAGE).convert("RGB"))
    rect = patches.Rectangle((80, 80), 8, 8, linewidth=2, edgecolor=RED, facecolor="none")
    axes[0].add_patch(rect)
    axes[0].set_title("A photo is really just a grid of numbers", fontsize=13, color=TEXT_PRIMARY)
    axes[0].axis("off")

    axes[1].imshow(patch, cmap="gray", vmin=0, vmax=255)
    for (j, i), val in np.ndenumerate(patch):
        color = "white" if val < 128 else "black"
        axes[1].text(i, j, str(val), ha="center", va="center", fontsize=9, color=color)
    axes[1].set_title("Zoomed 8×8 patch — each cell is one pixel's\nbrightness value (0 = black, 255 = white)",
                       fontsize=11, color=TEXT_PRIMARY)
    axes[1].set_xticks([])
    axes[1].set_yticks([])

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "pixel_grid.png"), dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("Saved pixel_grid.png")


# ---------------------------------------------------------------------------
# 2. RGB channel split
# ---------------------------------------------------------------------------
def gen_rgb_channels():
    img = Image.open(SAMPLE_IMAGE).convert("RGB").resize((224, 224))
    arr = np.array(img)

    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), facecolor=SURFACE)
    axes[0].imshow(arr)
    axes[0].set_title("Color image", fontsize=11, color=TEXT_PRIMARY)

    titles = ["Red channel", "Green channel", "Blue channel"]
    cmaps = ["Reds", "Greens", "Blues"]
    for i in range(3):
        axes[i + 1].imshow(arr[:, :, i], cmap=cmaps[i])
        axes[i + 1].set_title(titles[i], fontsize=11, color=TEXT_PRIMARY)

    for ax in axes:
        ax.axis("off")

    fig.suptitle("A color image = 3 stacked grids (channels): Red, Green, Blue",
                 fontsize=13, color=TEXT_PRIMARY, y=1.02)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "rgb_channels.png"), dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print("Saved rgb_channels.png")


# ---------------------------------------------------------------------------
# 3. Convolution illustration: kernel sliding over a grid
# ---------------------------------------------------------------------------
def gen_convolution():
    input_grid = np.array([
        [1, 1, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 1, 1],
        [0, 0, 1, 1, 0],
        [0, 1, 1, 0, 0],
    ])
    kernel = np.array([
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ])
    # valid convolution output at position (1,1) for illustration
    patch = input_grid[0:3, 0:3]
    output_val = int((patch * kernel).sum())

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), facecolor=SURFACE,
                              gridspec_kw={"width_ratios": [1.3, 1, 1]})

    ax = axes[0]
    ax.imshow(input_grid, cmap="Blues", vmin=-0.5, vmax=2)
    for (j, i), val in np.ndenumerate(input_grid):
        ax.text(i, j, str(val), ha="center", va="center", fontsize=13, color=TEXT_PRIMARY)
    rect = patches.Rectangle((-0.5, -0.5), 3, 3, linewidth=3, edgecolor=RED, facecolor="none")
    ax.add_patch(rect)
    ax.set_title("Input (a patch of the image)\nred box = filter's current position", fontsize=10.5)
    ax.set_xticks([]); ax.set_yticks([])

    ax = axes[1]
    ax.imshow(kernel, cmap="Oranges", vmin=-0.5, vmax=2)
    for (j, i), val in np.ndenumerate(kernel):
        ax.text(i, j, str(val), ha="center", va="center", fontsize=13, color=TEXT_PRIMARY)
    ax.set_title("Filter / kernel\n(the pattern it's looking for)", fontsize=10.5)
    ax.set_xticks([]); ax.set_yticks([])

    ax = axes[2]
    out_display = np.full((1, 1), output_val)
    ax.imshow(out_display, cmap="Greens", vmin=0, vmax=5)
    ax.text(0, 0, str(output_val), ha="center", va="center", fontsize=22, color=TEXT_PRIMARY)
    ax.set_title("Output (feature map value)\nmultiply overlapping cells, sum them up",
                 fontsize=10.5)
    ax.set_xticks([]); ax.set_yticks([])

    fig.suptitle("Convolution: a small filter slides across the image checking for a pattern",
                 fontsize=13, color=TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "convolution.png"), dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print("Saved convolution.png")


# ---------------------------------------------------------------------------
# 4. Train / Val / Test split (real counts)
# ---------------------------------------------------------------------------
def gen_split_chart():
    labels = ["Train\n(70%)", "Validation\n(15%)", "Test\n(15%)"]
    counts = [2147, 460, 460]
    colors = [BLUE, AQUA, YELLOW]

    fig, ax = plt.subplots(figsize=(8, 4), facecolor=SURFACE)
    bars = ax.bar(labels, counts, color=colors, width=0.55)
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{count:,} images", ha="center", fontsize=12, color=TEXT_PRIMARY)

    ax.set_facecolor(SURFACE)
    ax.set_ylim(0, 2500)
    ax.set_ylabel("Number of images", fontsize=11, color=TEXT_SECONDARY)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(MUTED)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=11)
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.set_title("3,067 fabric images split three ways", fontsize=13, color=TEXT_PRIMARY, pad=14)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "split_chart.png"), dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("Saved split_chart.png")


# ---------------------------------------------------------------------------
# 5. Real training curves from training_history.json
# ---------------------------------------------------------------------------
def gen_training_curves():
    with open(os.path.join(PROJECT_ROOT, "models", "training_history.json")) as f:
        history = json.load(f)

    epochs = [h["epoch"] for h in history]
    train_loss = [h["train_loss"] for h in history]
    val_loss = [h["val_loss"] for h in history]
    train_acc = [h["train_acc"] for h in history]
    val_acc = [h["val_acc"] for h in history]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), facecolor=SURFACE)

    ax = axes[0]
    ax.plot(epochs, train_loss, color=BLUE, linewidth=2.5, marker="o", markersize=4, label="Train loss")
    ax.plot(epochs, val_loss, color=RED, linewidth=2.5, marker="o", markersize=4, label="Validation loss")
    ax.set_title("Loss ↓ over training (lower = better)", fontsize=12, color=TEXT_PRIMARY)
    ax.set_xlabel("Epoch", color=TEXT_SECONDARY)
    ax.legend(frameon=False, fontsize=10)

    ax = axes[1]
    ax.plot(epochs, [a * 100 for a in train_acc], color=BLUE, linewidth=2.5, marker="o", markersize=4, label="Train accuracy")
    ax.plot(epochs, [a * 100 for a in val_acc], color=RED, linewidth=2.5, marker="o", markersize=4, label="Validation accuracy")
    ax.set_title("Accuracy ↑ over training (higher = better)", fontsize=12, color=TEXT_PRIMARY)
    ax.set_xlabel("Epoch", color=TEXT_SECONDARY)
    ax.set_ylabel("%", color=TEXT_SECONDARY)
    ax.legend(frameon=False, fontsize=10, loc="lower right")

    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color(MUTED)
        ax.tick_params(colors=TEXT_SECONDARY, labelsize=10)
        ax.yaxis.grid(True, color=GRID, linewidth=1)
        ax.set_axisbelow(True)

    fig.suptitle("Our actual training run: 12 epochs, ResNet18 head fine-tuned",
                 fontsize=13, color=TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "training_curves.png"), dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("Saved training_curves.png")


# ---------------------------------------------------------------------------
# 6. Annotated confusion matrix: recall (row) vs precision (column)
# ---------------------------------------------------------------------------
def gen_annotated_confusion():
    classes = ["Broken\nstitch", "Needle\nmark", "Pinched\nfabric", "Vertical",
               "defect\nfree", "hole", "horizontal", "lines", "stain"]
    matrix = np.array([
        [11, 2, 0, 0, 0, 0, 0, 0, 0],
        [1, 13, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 12, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 5, 0, 5, 4, 0, 0],
        [0, 0, 3, 0, 247, 0, 0, 0, 10],
        [0, 0, 0, 0, 0, 36, 1, 4, 0],
        [0, 0, 0, 2, 0, 9, 12, 1, 0],
        [0, 0, 0, 0, 0, 6, 0, 19, 0],
        [0, 0, 0, 0, 4, 0, 0, 0, 52],
    ])

    fig, ax = plt.subplots(figsize=(9, 7.2), facecolor=SURFACE)
    im = ax.imshow(matrix, cmap="Blues")

    for (j, i), val in np.ndenumerate(matrix):
        if val > 0:
            color = "white" if val > matrix.max() / 2 else TEXT_PRIMARY
            weight = "bold" if i == j else "normal"
            ax.text(i, j, str(val), ha="center", va="center", fontsize=10,
                     color=color, fontweight=weight)

    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes, fontsize=8.5, color=TEXT_SECONDARY)
    ax.set_yticklabels(classes, fontsize=8.5, color=TEXT_SECONDARY)
    ax.set_xlabel("Predicted class", fontsize=12, color=TEXT_PRIMARY)
    ax.set_ylabel("True class", fontsize=12, color=TEXT_PRIMARY)

    # Highlight the "Vertical" row (recall view) in red
    v_idx = classes.index("Vertical")
    ax.add_patch(patches.Rectangle((-0.5, v_idx - 0.5), len(classes), 1,
                                    fill=False, edgecolor=RED, linewidth=2.5))
    # Highlight the "hole" column (precision view) in violet
    h_idx = classes.index("hole")
    ax.add_patch(patches.Rectangle((h_idx - 0.5, -0.5), 1, len(classes),
                                    fill=False, edgecolor=VIOLET, linewidth=2.5))

    ax.set_title("Row (red) = recall view: of real 'Vertical' images, where did they go?\n"
                 "Column (violet) = precision view: of everything called 'hole', was it really hole?",
                 fontsize=10.5, color=TEXT_PRIMARY, pad=12)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "confusion_annotated.png"), dpi=200, facecolor=SURFACE)
    plt.close(fig)
    print("Saved confusion_annotated.png")


if __name__ == "__main__":
    gen_pixel_grid()
    gen_rgb_channels()
    gen_convolution()
    gen_split_chart()
    gen_training_curves()
    gen_annotated_confusion()
