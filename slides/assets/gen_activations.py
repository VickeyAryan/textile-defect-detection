"""Extract real early-layer vs late-layer feature map activations from our trained
ResNet18, on an actual sample image, to illustrate the CNN feature hierarchy with
genuine data instead of a generic diagram."""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from data_loader import build_transforms  # noqa: E402
from model import build_model  # noqa: E402

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
CHECKPOINT_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.pt")
SAMPLE_IMAGE = r"C:\Users\chirl\.cache\kagglehub\datasets\ziya07\multi-class-fabric-defect-detection-dataset\versions\3\Dataset\hole\1.jpg"
OUT_DIR = os.path.dirname(__file__)

TEXT_PRIMARY = "#0b0b0b"
SURFACE = "#fcfcfb"

checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
model = build_model(checkpoint["arch"], num_classes=len(checkpoint["class_names"]))
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

activations = {}


def hook(name):
    def _hook(module, inp, out):
        activations[name] = out.detach()
    return _hook


model.layer1.register_forward_hook(hook("early"))
model.layer4.register_forward_hook(hook("late"))

image = Image.open(SAMPLE_IMAGE).convert("RGB")
_, eval_tf = build_transforms(checkpoint["img_size"])
tensor = eval_tf(image).unsqueeze(0)

with torch.no_grad():
    model(tensor)

early = activations["early"].squeeze(0)  # [64, 56, 56]
late = activations["late"].squeeze(0)    # [512, 7, 7]

fig = plt.figure(figsize=(11, 4.6), facecolor=SURFACE)
gs = fig.add_gridspec(2, 7, height_ratios=[0.18, 1], hspace=0.15, wspace=0.08,
                       left=0.03, right=0.99, top=0.99, bottom=0.03)

# Original image spans the leftmost column across both rows conceptually;
# simplest: separate figure regions using subplot2grid instead.
plt.close(fig)

fig = plt.figure(figsize=(11, 4.8), facecolor=SURFACE)

ax_img = plt.subplot2grid((2, 8), (0, 0), rowspan=2, fig=fig)
ax_img.imshow(image.resize((224, 224)))
ax_img.set_title("Input image\n(true class: hole)", fontsize=10, color=TEXT_PRIMARY)
ax_img.axis("off")

n_maps = 6
for i in range(n_maps):
    ax = plt.subplot2grid((2, 8), (0, i + 1), fig=fig)
    ax.imshow(early[i].numpy(), cmap="Blues")
    ax.axis("off")
    if i == n_maps // 2 - 1:
        ax.set_title("Early layer (layer1) — simple patterns: edges, weave texture",
                      fontsize=9.5, color=TEXT_PRIMARY, loc="left")

for i in range(n_maps):
    ax = plt.subplot2grid((2, 8), (1, i + 1), fig=fig)
    ax.imshow(late[i * 8].numpy(), cmap="Purples")
    ax.axis("off")
    if i == n_maps // 2 - 1:
        ax.set_title("Late layer (layer4) — abstract, defect-shaped patterns",
                      fontsize=9.5, color=TEXT_PRIMARY, loc="left")

fig.savefig(os.path.join(OUT_DIR, "feature_hierarchy.png"), dpi=200, facecolor=SURFACE)
print("Saved feature_hierarchy.png")
