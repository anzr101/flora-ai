"""Tests for the group-aware split and the model factory.

torch is heavy and excluded from CI; these tests skip cleanly when it is absent.
The group-split test needs only numpy and runs everywhere.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from floradl.data import _grouped_split, group_key


def test_group_key_strips_variant_suffixes():
    assert group_key("plant7_img3.jpg") == "plant7"
    assert group_key("leafA_aug12.png") == "leafA"
    assert group_key("photo (2).jpg") == "photo"


def test_grouped_split_keeps_groups_disjoint():
    # 30 groups, 4 images each; the same group must never cross splits.
    files = [Path(f"plant{g}_img{j}.jpg") for g in range(30) for j in range(4)]
    rng = np.random.default_rng(0)
    train, val, test = _grouped_split(files, rng)

    def groups(fs):
        return {group_key(f.name) for f in fs}

    g_train, g_val, g_test = groups(train), groups(val), groups(test)
    assert g_train & g_test == set(), "train/test leak a group!"
    assert g_train & g_val == set()
    assert g_val & g_test == set()
    assert len(train) + len(val) + len(test) == len(files)


def test_model_builds_and_forward_pass():
    torch = pytest.importorskip("torch")
    from floradl.model import build_model

    model = build_model(num_classes=4, arch="mobilenet_v3_small", pretrained=False)
    model.eval()
    out = model(torch.randn(2, 3, 224, 224))
    assert out.shape == (2, 4)

    # Only the classifier head should be trainable (backbone frozen).
    trainable = [n for n, p in model.named_parameters() if p.requires_grad]
    assert trainable, "head must be trainable"
    assert all("classifier" in n for n in trainable), "only the head should train"
