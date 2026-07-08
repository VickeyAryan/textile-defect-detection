"""Evaluate a trained checkpoint on the test set: accuracy, confusion matrix, per-class metrics.

Usage:
    python src/evaluate.py --data-dir data/ --checkpoint models/best_model.pt
"""

import argparse
import os

import matplotlib.pyplot as plt
import seaborn as sns
import torch
from sklearn.metrics import classification_report, confusion_matrix

from data_loader import get_dataloaders
from model import build_model


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate the fabric defect classifier.")
    parser.add_argument("--data-dir", type=str, default="data")
    parser.add_argument("--checkpoint", type=str, default="models/best_model.pt")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output-dir", type=str, default="models")
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    class_names = checkpoint["class_names"]
    img_size = checkpoint["img_size"]

    _, _, test_loader, loaded_classes = get_dataloaders(
        args.data_dir, batch_size=args.batch_size, img_size=img_size
    )
    assert loaded_classes == class_names, "Class order mismatch between checkpoint and dataset."

    model = build_model(checkpoint["arch"], num_classes=len(class_names)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(1).cpu()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    accuracy = sum(p == l for p, l in zip(all_preds, all_labels)) / len(all_labels)
    print(f"Test accuracy: {accuracy:.4f}\n")

    report = classification_report(all_labels, all_preds, target_names=class_names, digits=4)
    print(report)

    os.makedirs(args.output_dir, exist_ok=True)
    with open(os.path.join(args.output_dir, "classification_report.txt"), "w") as f:
        f.write(f"Test accuracy: {accuracy:.4f}\n\n{report}")

    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(max(6, len(class_names)), max(5, len(class_names) * 0.8)))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"Confusion Matrix (test accuracy={accuracy:.4f})")
    plt.tight_layout()
    cm_path = os.path.join(args.output_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    print(f"\nConfusion matrix saved to {cm_path}")
    print(f"Classification report saved to {os.path.join(args.output_dir, 'classification_report.txt')}")


if __name__ == "__main__":
    main()
