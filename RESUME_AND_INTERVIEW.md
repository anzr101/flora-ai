# FloraAI — Resume & Interview Guide

This is the "how to present it" companion to the code. It answers: *should this
go on my resume, how do I phrase it, and what will I be asked?*

---

## 1. Should you put FloraAI on your resume?

**Yes — as your ONE flagship project**, presented as a *system*, not three demos.
Two conditions keep it credible:

1. **Deploy at least one module to a live URL** before you lead with it (the ML
   service is the easiest — it trains in ~80s and has no GPU needs). A live link
   beats any bullet point.
2. **Never overstate the data.** The ML data is synthetic (by a documented causal
   process) and the DL model is a pipeline you train, not pretrained weights you
   benchmarked on a public leaderboard. Say so. Honesty here is a *strength* —
   it signals you understand provenance and leakage, which is rarer than it
   should be.

Why it works across the roles you're targeting:
- **ML Engineer / Applied AI:** full tabular lifecycle with leakage control,
  benchmarking, SHAP, and a served model.
- **AI Engineer / GenAI:** an agent with RAG, tool-calling, and an eval harness.
- **MLOps:** four containerised services, a gateway, health checks, CI, config.

---

## 2. Resume entry (copy/adapt)

> **FloraAI — End-to-end botanical AI platform** · *Python, scikit-learn,
> PyTorch, FastAPI, Anthropic Claude, Docker* · [github.com/you/flora_ai]
> - Architected a 4-service AI platform: classical ML (structured health-risk
>   prediction), deep-learning vision (transfer-learned leaf classifier), and an
>   agentic RAG assistant, fused behind a FastAPI orchestration gateway.
> - Built a **leakage-safe** tabular ML pipeline (preprocessing inside the
>   sklearn Pipeline, stratified CV, model benchmarking) reaching **0.72 macro-F1**
>   with **SHAP** explanations served per prediction.
> - Implemented **transfer learning** (MobileNetV3) with a **group-aware split**
>   and an out-of-distribution test to report honest, non-leaked accuracy; added
>   confidence-based abstention for OOD images.
> - Engineered a **RAG agent** (local ONNX embeddings + Claude, cost-optimised)
>   with tool-calling into the ML service and a retrieval **eval harness**
>   (hit@k / MRR) — **hit@4 = 1.0** on a labelled gold set.
> - Containerised every service with health checks, config via env, and CI.

Trim to 3–4 bullets for space; keep one metric per bullet.

---

## 3. The 60-second pitch (interview opener)

> "FloraAI is an end-to-end AI platform for plant care. Rather than forcing one
> technique everywhere, I used the right paradigm for each problem: classical
> gradient-boosted trees for structured health prediction, a transfer-learned
> CNN for leaf images, and a RAG agent on Claude for open-ended reasoning. A
> FastAPI gateway orchestrates them — you upload a photo and conditions, the
> vision and ML models run, and the agent fuses everything into grounded care
> advice with citations. Each service is independently deployable and
> containerised. I was deliberate about correctness: no data leakage, a
> group-aware image split, an out-of-distribution test, and an eval harness for
> the RAG retrieval."

---

## 4. Questions you WILL be asked (and strong answers)

**Q: Your data is synthetic — isn't that a weakness?**
> Public tabular "plant health" datasets are themselves synthetic and of unknown
> provenance, so I generated mine from an explicit causal process instead. The
> upside: I know the ground truth, so I can verify the model recovers the real
> drivers (SHAP ranks the features the DGP actually uses). I'd swap in a real
> agronomy dataset for production; the pipeline is data-agnostic.

**Q: How did you prevent data leakage?**
> Tabular: all preprocessing (impute/scale) lives inside the sklearn Pipeline, so
> during cross-validation it's fit on training folds only — test statistics never
> leak. Vision: I split by *group* (leaf id from the filename) so augmentations
> of the same leaf can't span train and test. A random split there inflates
> PlantVillage accuracy to a meaningless 99%.

**Q: Why did the tree model beat logistic regression?**
> The target has a real interaction — heat stress is worse in dry soil — which is
> non-linear. LogReg (a linear baseline) plateaus around 0.66 macro-F1; HistGBM
> captures the interaction and reaches ~0.72. I kept LogReg specifically as an
> honest baseline to show the gain is real, not assumed.

**Q: How do you know your RAG isn't hallucinating?**
> Two things: every answer returns citations to the source chunks, and I have an
> eval harness that scores retrieval (hit@k, MRR) against a labelled gold set —
> retrieval is the foundation, so I measure it rather than eyeballing. Next step
> would be an LLM-judge groundedness score on generated answers.

**Q: Why local embeddings instead of an API?**
> Claude has no embeddings endpoint, and embedding a static knowledge base per
> token would be pure cost. Local ONNX embeddings (fastembed) are free, fast on
> CPU, and keep the container torch-free. Claude is used only where it adds value
> — generation and tool orchestration.

**Q: What happens if a service is down?**
> The gateway degrades gracefully — each downstream call is wrapped, so a failure
> becomes a partial result plus a templated fallback, not a 500. Partial answers
> beat a hard failure for users.

**Q: How would you productionise this further?**
> Add auth + rate limiting at the gateway, a managed vector DB if the corpus
> grows, model/data drift monitoring (Evidently/Prometheus), and a model registry
> + retraining pipeline. The architecture already isolates these concerns per
> service.

**Q: Confidence/abstention — why?**
> A classifier is overconfident on out-of-distribution inputs. Below a softmax
> threshold the vision API flags `low_confidence` instead of asserting a label,
> and the gateway tells the agent to treat the species as uncertain. Calibrated
> humility is more useful than a confident wrong answer.

---

## 5. Honest limitations to state proactively (this builds trust)

- Synthetic tabular data (documented), not real observational data.
- DL ships as a reproducible training pipeline, not pretrained weights.
- Monitoring/drift is designed-for but stubbed, not wired to a live dashboard.
- No auth/rate-limiting yet — it's a portfolio platform, not a hardened product.

Stating these *before* you're asked signals senior judgement.

---

## 6. What to build next (if you want to go further)

1. Deploy ML + gateway to a free host (Render/Railway) and put the URL on the CV.
2. Train the DL model on real PlantVillage + a small field-photo OOD set; publish
   the in-distribution vs OOD accuracy gap — that single honest chart is gold.
3. Add an LLM-judge groundedness metric to the RAG eval.
4. A tiny React/Streamlit demo UI over the gateway for screen-share interviews.
