"""Image transforms — shared between training and inference so preprocessing can
never drift between the two (a subtle but common source of train/serve skew).

Training applies augmentation (random crop/flip/colour jitter) to improve
generalisation; validation and inference apply only deterministic resize +
normalisation with the same ImageNet statistics the backbone was trained on.
"""

from __future__ import annotations

from torchvision import transforms

from floradl.config import IMAGENET_MEAN, IMAGENET_STD, settings


def build_transforms(train: bool):
    size = settings.image_size
    if train:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(size, scale=(0.7, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.ToTensor(),
                transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
            ]
        )
    return transforms.Compose(
        [
            transforms.Resize(int(size * 1.15)),
            transforms.CenterCrop(size),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
