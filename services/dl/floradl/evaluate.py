"""Evaluate a trained checkpoint, including an OPTIONAL out-of-distribution test.

The headline number from `train.py` is in-distribution test accuracy (same
source as training). The honest question is: how well does it do on *real-world*
photos it has never seen the style of? Point `--ood` at a folder of field photos
(ImageFolder layout with the same class names) to measure the drop. Surfacing
that gap is the point — it is what separates honest CV from a leaderboard score.

Run:  python -m floradl.evaluate
      python -m floradl.evaluate --ood path/to/field_photos
"""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from floradl.config import SPLIT_DIR, settings
from floradl.inference import get_classifier
from floradl.transforms import build_transforms


@torch.no_grad()
def _accuracy_on_folder(folder: Path) -> float:
    clf = get_classifier()
    ds = ImageFolder(folder, transform=build_transforms(train=False))
    loader = DataLoader(ds, batch_size=settings.batch_size, num_workers=settings.num_workers)
    correct = total = 0
    for x, y in loader:
        x = x.to(clf.device)
        preds = clf.model(x).argmax(1).cpu()
        correct += (preds == y).sum().item()
        total += y.numel()
    return correct / max(total, 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ood", type=str, default=None, help="folder of out-of-distribution photos")
    args = ap.parse_args()

    test_dir = SPLIT_DIR / "test"
    if test_dir.exists():
        acc = _accuracy_on_folder(test_dir)
        print(f"In-distribution test accuracy : {acc:.4f}")

    if args.ood:
        ood_acc = _accuracy_on_folder(Path(args.ood))
        print(f"Out-of-distribution accuracy  : {ood_acc:.4f}")
        print("NOTE: a large drop here is expected and HONEST — it reveals reliance "
              "on dataset artifacts (e.g. uniform backgrounds in PlantVillage).")


if __name__ == "__main__":
    main()
