# FloraAI · Module 2 — Deep Learning (Computer Vision)

**Problem:** classify a plant/leaf **image** into a species/disease class.

**Why deep learning:** images are high-dimensional with spatial structure that
convolutions exploit — classical ML cannot. We use **transfer learning** from an
ImageNet-pretrained backbone, which is the data-efficient, production-standard
approach.

## The two decisions that make this honest
1. **Group-aware split** (`data.py`): the same physical leaf never spans
   train/val/test, so accuracy reflects generalisation, not memorisation of
   near-duplicate augmentations. A naive random split inflates PlantVillage
   accuracy to a meaningless ~99%.
2. **Out-of-distribution test** (`evaluate.py --ood`): report accuracy on
   real-world field photos, not just clean studio images. The drop is expected
   and is the point — PlantVillage models are known to cheat off backgrounds.
3. **Abstention** (`inference.py`): below a confidence threshold the API returns
   `low_confidence=True` instead of a confident wrong label.

## Run

```bash
pip install -r requirements.txt        # CPU torch by default

# Option A — real data: drop PlantVillage into data/raw/<class>/*.jpg, then:
python -m floradl.data --prepare

# Option B — smoke test the whole pipeline with synthetic data:
python -m floradl.data --synthetic
python -m floradl.data --prepare

python -m floradl.train                # transfer learning -> models/species.pt
python -m floradl.evaluate             # in-distribution test acc
python -m floradl.evaluate --ood <dir> # out-of-distribution drop
uvicorn floradl.api:app --port 8002    # http://localhost:8002/docs
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
