# Fabric Defect Detector

A computer vision project that classifies fabric images as **defect-free** or **defective** (with defect type), using transfer learning on a pretrained CNN. Built as a learning project and portfolio piece connecting deep learning with textile/apparel quality control.

## Problem Statement

Manual fabric inspection in textile manufacturing is slow and inconsistent. This project explores whether a lightweight, pretrained computer vision model can be fine-tuned to automatically classify common fabric defects (holes, lines, stains, etc.) from photographs — a task relevant to textile QC and export compliance workflows.

## Dataset

**Multi-Class Fabric Defect Detection Dataset** (Kaggle)
- 3,077 high-resolution fabric images
- 9 classes: defect-free, hole, horizontal, vertical, lines, pinched fabric, needle mark, and others
- Source: real production-line captures (Basler industrial cameras)
- Link: https://www.kaggle.com/datasets/ziya07/multi-class-fabric-defect-detection-dataset

Downloaded programmatically via `kagglehub` (see Setup below) — no manual download required.

## Approach

- **Transfer learning**: fine-tune a pretrained CNN (ResNet18 or MobileNetV2) rather than training from scratch, since the dataset is small and compute is limited (CPU-only local machine)
- **Training environment**: Google Colab (free GPU) for the training step; local machine for data prep, inference, and the demo app
- **Framework**: PyTorch + torchvision

## Project Structure

```
fabric-defect-detector/
├── data/                  # downloaded dataset (gitignored)
├── notebooks/
│   └── train_model.ipynb  # Colab training notebook
├── src/
│   ├── data_loader.py     # dataset loading & preprocessing
│   ├── model.py           # model definition (pretrained backbone + fine-tuned head)
│   ├── train.py           # training loop
│   └── evaluate.py        # accuracy, confusion matrix, per-class metrics
├── app/
│   └── streamlit_app.py   # drag-and-drop demo: upload image -> get prediction
├── models/
│   └── best_model.pt      # saved fine-tuned model weights
├── requirements.txt
└── README.md
```

## Setup

```bash
# clone and enter project
git clone <repo-url>
cd fabric-defect-detector

# create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# install dependencies
pip install -r requirements.txt
```

Download the dataset (requires a Kaggle API token in `~/.kaggle/kaggle.json`):
```python
import kagglehub
path = kagglehub.dataset_download("ziya07/multi-class-fabric-defect-detection-dataset")
print(path)  # e.g. ~/.cache/kagglehub/datasets/ziya07/.../versions/3/Dataset
```
The dataset is a flat `Dataset/<class_name>/*.jpg` layout (no pre-existing train/val/test split)
`src/data_loader.py` splits it into train/val/test automatically (70/15/15).

## Usage

**Train the model:**
```bash
python src/train.py --data-dir <path-from-kagglehub> --arch resnet18 --epochs 15
```
Recommended: run `notebooks/train_model.ipynb` on Google Colab for GPU access, which fine-tunes
the full backbone. Locally on CPU, add `--freeze-backbone` to only train the classification head
(much faster, see Results below for what that trades off).

**Evaluate on the test set:**
```bash
python src/evaluate.py --data-dir <path-from-kagglehub> --checkpoint models/best_model.pt
```

**Run the demo app locally:**
```bash
streamlit run app/streamlit_app.py
```
Upload a fabric image and get a predicted class with confidence score.

## Results

Trained locally on CPU: ResNet18 backbone frozen (ImageNet weights), only the final
classification head fine-tuned, 8 epochs (early-stopped from a 12-epoch budget, patience 4),
batch size 32, Adam lr=1e-3.

- **Validation accuracy:** 90.0%
- **Test accuracy:** 88.5% (460 held-out images)

Per-class test performance (precision / recall / F1):

| Class          | Precision | Recall | F1   | Support |
|----------------|-----------|--------|------|---------|
| defect free    | 0.984     | 0.950  | 0.967| 260     |
| stain          | 0.839     | 0.929  | 0.881| 56      |
| Needle mark    | 0.867     | 0.929  | 0.897| 14      |
| Broken stitch  | 0.846     | 0.846  | 0.846| 13      |
| Pinched fabric | 0.800     | 0.923  | 0.857| 13      |
| lines          | 0.792     | 0.760  | 0.776| 25      |
| hole           | 0.643     | 0.878  | 0.742| 41      |
| horizontal     | 0.706     | 0.500  | 0.585| 24      |
| Vertical       | 0.714     | 0.357  | 0.476| 14      |

The model is strong on `defect free` and `stain` (largest classes) but weaker on the small,
visually-similar defect types — `Vertical`, `horizontal`, `hole`, and `lines` are often confused
with each other (e.g. Vertical predicted as hole/horizontal, hole predicted as horizontal/lines),
which tracks with the dataset's class imbalance (`defect free` alone is ~54% of the data,
`Vertical` only ~3%) and the visual similarity of directional line-type defects.

Since only the classification head was trained (backbone frozen, for CPU speed), fine-tuning the
full backbone on a GPU — using `notebooks/train_model.ipynb` on Colab — should improve the
weaker classes further; that notebook trains with the backbone unfrozen by default.

See `models/confusion_matrix.png` and `models/classification_report.txt` for full details.

## What This Project Demonstrates

- Image classification via transfer learning (pretrained CNN fine-tuning)
- End-to-end ML pipeline: data loading → training → evaluation → deployment (demo app)
- Practical handling of a real-world, imbalanced industrial dataset

## Future Improvements

- Object detection (localize the defect, not just classify the whole image) using YOLOv8
- Expand to defect segmentation (pixel-level defect boundaries)
- Deploy as a hosted web app rather than local Streamlit

## Tech Stack

Python · PyTorch · torchvision · Streamlit · scikit-learn (metrics) · kagglehub

## License

MIT
