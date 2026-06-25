"""Dataset preparation with a GROUP-AWARE split — the key correctness decision
for this module.

WHY GROUP-AWARE
---------------
Datasets like PlantVillage contain multiple photos/augmentations of the *same*
physical leaf. A naive random train/test split leaks near-duplicate images
across the boundary, inflating test accuracy to a meaningless ~99%. We therefore
split by *group* (a leaf/source id derived from the filename) so the same leaf
never appears in more than one split. Reported accuracy then reflects
generalisation to unseen plants, not memorisation.

Expected raw layout (ImageFolder):  data/raw/<class_name>/<image>.jpg

This module also generates a small SYNTHETIC dataset so the whole pipeline can be
smoke-tested end-to-end without downloading PlantVillage.

Run:  python -m floradl.data --prepare        # split data/raw into processed/
      python -m floradl.data --synthetic      # create a tiny synthetic dataset
"""

from __future__ import annotations

import argparse
import re
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np

from floradl.config import RAW_DIR, SPLIT_DIR, settings

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def group_key(filename: str) -> str:
    """Derive a stable group id from an image filename.

    Default heuristic: strip common augmentation/copy suffixes so variants of one
    source image share a key. Falls back to the bare stem. For a specific dataset
    you would tune this regex to the dataset's naming scheme.
    """
    stem = Path(filename).stem
    # Synthetic + many real schemes: '<group>_img3', '<group>_aug2', '<group> (1)'
    stem = re.sub(r"[_-](img|aug|copy|var)\d+$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"\s*\(\d+\)$", "", stem)
    return stem


def _grouped_split(files: list[Path], rng: np.random.Generator):
    """Split file paths into (train, val, test) so groups never cross splits."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in files:
        groups[group_key(f.name)].append(f)

    keys = list(groups)
    rng.shuffle(keys)
    n = len(keys)
    n_test = max(1, int(n * settings.test_fraction))
    n_val = max(1, int(n * settings.val_fraction))

    test_keys = set(keys[:n_test])
    val_keys = set(keys[n_test : n_test + n_val])

    train, val, test = [], [], []
    for k, fs in groups.items():
        target = test if k in test_keys else val if k in val_keys else train
        target.extend(fs)
    return train, val, test


def prepare() -> dict:
    """Build data/processed/{train,val,test}/<class>/ from data/raw/."""
    if not RAW_DIR.exists():
        raise SystemExit(
            f"No raw data at {RAW_DIR}. Place ImageFolder data there, or run "
            f"`python -m floradl.data --synthetic` for a smoke-test dataset."
        )

    rng = np.random.default_rng(settings.seed)
    classes = sorted([d.name for d in RAW_DIR.iterdir() if d.is_dir()])
    if not classes:
        raise SystemExit(f"No class subfolders found under {RAW_DIR}.")

    if SPLIT_DIR.exists():
        shutil.rmtree(SPLIT_DIR)

    counts = {"train": 0, "val": 0, "test": 0}
    for cls in classes:
        files = [f for f in (RAW_DIR / cls).iterdir() if f.suffix.lower() in IMAGE_EXTS]
        train, val, test = _grouped_split(files, rng)
        for split_name, split_files in (("train", train), ("val", val), ("test", test)):
            dest = SPLIT_DIR / split_name / cls
            dest.mkdir(parents=True, exist_ok=True)
            for f in split_files:
                shutil.copy2(f, dest / f.name)
            counts[split_name] += len(split_files)

    print(f"Classes: {classes}")
    print(f"Split counts: {counts}  ->  {SPLIT_DIR}")
    return {"classes": classes, "counts": counts}


def make_synthetic(n_classes: int = 4, groups_per_class: int = 12, imgs_per_group: int = 5) -> None:
    """Create a tiny synthetic ImageFolder dataset for smoke-testing the pipeline.

    Each class has a distinct base colour; each 'group' (a fake plant) gets a few
    noisy variants sharing a group id in the filename, so group-aware splitting is
    actually exercised.
    """
    from PIL import Image

    rng = np.random.default_rng(settings.seed)
    if RAW_DIR.exists():
        shutil.rmtree(RAW_DIR)

    base_colors = rng.integers(40, 215, size=(n_classes, 3))
    for c in range(n_classes):
        cls_dir = RAW_DIR / f"class_{c}"
        cls_dir.mkdir(parents=True, exist_ok=True)
        for g in range(groups_per_class):
            for j in range(imgs_per_group):
                arr = base_colors[c] + rng.normal(0, 18, size=(64, 64, 3))
                arr = np.clip(arr, 0, 255).astype(np.uint8)
                Image.fromarray(arr).save(cls_dir / f"plant{g}_img{j}.jpg")
    total = n_classes * groups_per_class * imgs_per_group
    print(f"Wrote {total} synthetic images across {n_classes} classes -> {RAW_DIR}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", action="store_true", help="split raw/ into processed/")
    ap.add_argument("--synthetic", action="store_true", help="generate a synthetic dataset")
    args = ap.parse_args()
    if args.synthetic:
        make_synthetic()
    if args.prepare or not (args.prepare or args.synthetic):
        prepare()


if __name__ == "__main__":
    main()
