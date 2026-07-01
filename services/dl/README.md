# FloraAI · Module 2 — Deep Learning (Computer Vision)

**Problem:** identify the plant **species** in an image.

**Two backends** (choose with `FLORA_DL_IDENTIFIER_BACKEND`):

1. **`bioclip` (default, served):** open-ended identification with **BioCLIP** — a
   CLIP-style vision model pre-trained on 10M images across the biological tree of
   life. It matches a photo against ~450,000 species with no task-specific
   training, so it works on real photos of any plant. See `bioclip_backend.py`.
2. **`cnn` (baseline):** a **transfer-learning** classifier I built end-to-end
   (frozen ImageNet MobileNetV3 backbone + a fresh head) to demonstrate the
   supervised CV lifecycle. See `model.py`, `train.py`.

**Why two:** BioCLIP gives real-world accuracy without a labelled dataset; the CNN
pipeline shows the fundamentals (data → transfer learning → evaluation → serving).

## Good-practice decisions in the CNN pipeline (interview-relevant)
1. **Group-aware split** (`data.py`): the same physical leaf never spans
   train/val/test, so accuracy reflects generalisation, not memorisation of
   near-duplicate augmentations. A naive random split inflates accuracy.
2. **Out-of-distribution test** (`evaluate.py --ood`): report accuracy on
   real-world photos, not just clean studio images — the honest number.
3. **Abstention** (both backends): below a confidence threshold the API returns
   `low_confidence=True` instead of a confident wrong label.

## Run

```bash
pip install -r requirements.txt        # CPU torch by default

# Default backend is BioCLIP — no training needed, just serve:
uvicorn floradl.api:app --port 8002    # http://localhost:8002/docs

# To train + serve the CNN baseline instead:
python -m floradl.data --synthetic     # (or drop real images in data/raw/<class>/)
python -m floradl.data --prepare
python -m floradl.train                # transfer learning -> models/species.pt
FLORA_DL_IDENTIFIER_BACKEND=cnn uvicorn floradl.api:app --port 8002
pytest                                 # split + model tests
```

## Example request

```bash
curl -X POST localhost:8002/identify -F "file=@leaf.jpg"
```

Returns the predicted class, confidence, top-k, model version, and a
`low_confidence` flag.

## Architectures
Config-driven (`FLORA_DL_ARCH`): `mobilenet_v3_small` (default, fast),
`resnet18`, or `efficientnet_b0`. The backbone is frozen; only the classifier
head trains (optional full fine-tuning via `model.unfreeze_backbone`).
