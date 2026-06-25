"""Transfer-learning training loop with validation-based early stopping.

Reads data/processed/{train,val,test}/ (created by data.py's group-aware split),
trains a fresh classifier head on a frozen ImageNet backbone, keeps the best
checkpoint by validation accuracy, then reports held-out test accuracy.

Run:  python -m floradl.train
"""

from __future__ import annotations

import json
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

from floradl.config import CHECKPOINT, MODELS_DIR, SPLIT_DIR, settings
from floradl.model import build_model, device
from floradl.transforms import build_transforms


def _loaders():
    if not (SPLIT_DIR / "train").exists():
        raise SystemExit(
            f"No processed data at {SPLIT_DIR}. Run `python -m floradl.data --prepare` "
            f"(or `--synthetic` then `--prepare`) first."
        )
    train_ds = ImageFolder(SPLIT_DIR / "train", transform=build_transforms(train=True))
    val_ds = ImageFolder(SPLIT_DIR / "val", transform=build_transforms(train=False))
    test_ds = ImageFolder(SPLIT_DIR / "test", transform=build_transforms(train=False))

    common = dict(batch_size=settings.batch_size, num_workers=settings.num_workers)
    return (
        DataLoader(train_ds, shuffle=True, **common),
        DataLoader(val_ds, shuffle=False, **common),
        DataLoader(test_ds, shuffle=False, **common),
        train_ds.classes,
    )


@torch.no_grad()
def _evaluate(model, loader, dev) -> float:
    model.eval()
    correct = total = 0
    for x, y in loader:
        x, y = x.to(dev), y.to(dev)
        preds = model(x).argmax(1)
        correct += (preds == y).sum().item()
        total += y.numel()
    return correct / max(total, 1)


def train() -> dict:
    torch.manual_seed(settings.seed)
    dev = device()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    train_loader, val_loader, test_loader, classes = _loaders()
    model = build_model(num_classes=len(classes)).to(dev)

    criterion = nn.CrossEntropyLoss()
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(params, lr=settings.lr)

    best_val, best_state, history = 0.0, None, []
    print(f"Device={dev}  arch={settings.arch}  classes={classes}")
    for epoch in range(1, settings.epochs + 1):
        model.train()
        running = 0.0
        for x, y in train_loader:
            x, y = x.to(dev), y.to(dev)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            running += loss.item() * x.size(0)

        train_loss = running / len(train_loader.dataset)
        val_acc = _evaluate(model, val_loader, dev)
        history.append({"epoch": epoch, "train_loss": round(train_loss, 4), "val_acc": round(val_acc, 4)})
        print(f"  epoch {epoch:>2}  train_loss={train_loss:.4f}  val_acc={val_acc:.4f}")

        if val_acc >= best_val:  # keep the best-generalising weights
            best_val = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)
    test_acc = _evaluate(model, test_loader, dev)
    print(f"Best val_acc={best_val:.4f}  |  held-out test_acc={test_acc:.4f}")

    torch.save(
        {
            "state_dict": model.state_dict(),
            "classes": classes,
            "arch": settings.arch,
            "image_size": settings.image_size,
            "metrics": {"best_val_acc": best_val, "test_acc": test_acc, "history": history},
            "version": f"{settings.arch}-v1",
        },
        CHECKPOINT,
    )
    (MODELS_DIR / "metrics.json").write_text(
        json.dumps({"best_val_acc": best_val, "test_acc": test_acc, "classes": classes}, indent=2)
    )
    print(f"Saved checkpoint -> {CHECKPOINT}")
    return {"best_val_acc": best_val, "test_acc": test_acc, "classes": classes}


def main() -> None:
    t0 = time.time()
    train()
    print(f"Done in {time.time() - t0:.1f}s.")


if __name__ == "__main__":
    main()
