"""Model definition: pretrained CNN backbone with a fine-tuned classification head."""

import torch.nn as nn
from torchvision import models


SUPPORTED_ARCHS = ("resnet18", "mobilenet_v2")


def build_model(arch: str = "resnet18", num_classes: int = 9, freeze_backbone: bool = False) -> nn.Module:
    """Build a pretrained torchvision backbone with its final layer replaced for num_classes.

    Args:
        arch: "resnet18" or "mobilenet_v2".
        num_classes: number of output classes.
        freeze_backbone: if True, only the new head is trainable (faster, less prone to
            overfitting on small datasets); if False, the whole network is fine-tuned.
    """
    if arch not in SUPPORTED_ARCHS:
        raise ValueError(f"Unsupported arch '{arch}'. Choose from {SUPPORTED_ARCHS}.")

    if arch == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:  # mobilenet_v2
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
        if freeze_backbone:
            for param in model.parameters():
                param.requires_grad = False
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

    return model
