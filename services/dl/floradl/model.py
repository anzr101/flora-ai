"""Model factory: transfer learning from ImageNet-pretrained backbones.

We freeze the convolutional backbone and train a fresh classifier head. This is
the right call for a modest dataset: the backbone already encodes generic visual
features (edges, textures, leaf-like shapes), so we only learn the mapping from
those features to our classes — far less data-hungry and faster than training
from scratch. `unfreeze_backbone` enables optional fine-tuning later.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torchvision.models as tvm

from floradl.config import settings


def build_model(num_classes: int, arch: str | None = None, pretrained: bool = True) -> nn.Module:
    arch = arch or settings.arch

    if arch == "mobilenet_v3_small":
        weights = tvm.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
        model = tvm.mobilenet_v3_small(weights=weights)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
        head_params = model.classifier.parameters()

    elif arch == "resnet18":
        weights = tvm.ResNet18_Weights.DEFAULT if pretrained else None
        model = tvm.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
        head_params = model.fc.parameters()

    elif arch == "efficientnet_b0":
        weights = tvm.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = tvm.efficientnet_b0(weights=weights)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
        head_params = model.classifier.parameters()

    else:
        raise ValueError(f"Unsupported arch: {arch}")

    # Freeze everything, then re-enable gradients on the new head only.
    for p in model.parameters():
        p.requires_grad = False
    for p in head_params:
        p.requires_grad = True

    return model


def unfreeze_backbone(model: nn.Module) -> None:
    """Enable gradients on all layers for an optional fine-tuning phase."""
    for p in model.parameters():
        p.requires_grad = True


def device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")
