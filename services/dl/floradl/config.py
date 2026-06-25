"""Configuration for the DL service."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

SERVICE_ROOT = Path(__file__).resolve().parent.parent  # services/dl/
DATA_DIR = SERVICE_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"          # ImageFolder: raw/<class_name>/<image>.jpg
SPLIT_DIR = DATA_DIR / "processed"  # train/ val/ test/ created by data.py
MODELS_DIR = SERVICE_ROOT / "models"
CHECKPOINT = MODELS_DIR / "species.pt"

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


class DLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FLORA_DL_", extra="ignore")

    seed: int = 42
    arch: str = "mobilenet_v3_small"  # mobilenet_v3_small | resnet18 | efficientnet_b0
    image_size: int = 224
    batch_size: int = 32
    epochs: int = 8
    lr: float = 1e-3
    val_fraction: float = 0.15
    test_fraction: float = 0.15
    # Below this softmax probability the API abstains (low_confidence=True) —
    # the honest response to an out-of-distribution photo.
    confidence_threshold: float = 0.55
    num_workers: int = 0  # 0 is safest cross-platform (Windows spawn issues)

    # Which identifier the API serves:
    #   "clip" → CLIP zero-shot, open-vocabulary, works on REAL photos (default)
    #   "cnn"  → the supervised transfer-learning model (needs a trained checkpoint)
    identifier_backend: str = "clip"

    # CLIP zero-shot settings. ViT-L-14 is far stronger at fine-grained plant
    # discrimination than ViT-B-32 (which confuses e.g. Monstera with ferns).
    clip_model: str = "ViT-L-14"
    clip_pretrained: str = "laion2b_s32b_b82k"
    clip_confidence_threshold: float = 0.30  # 15+ classes → random ≈ 0.06


settings = DLSettings()
