# Module 1 — Adversarial Machine Learning

Four short, self-contained Jupyter notebooks for a ~20-minute live walkthrough of adversarial ML:
what the attacks are, how they work, how they transfer, and what defenses (don't) do.

| # | Notebook | Run | What it shows | Live time | Run time (laptop CPU) |
|---|---|---|---|---|---|
| 1 | [`01_adversarial_examples_images.ipynb`](01_adversarial_examples_images.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/01_adversarial_examples_images.ipynb) | FGSM & PGD on an MNIST CNN, accuracy-vs-ε curve, untargeted vs targeted attacks side by side, **transferability matrix** across 3 models, adversarial training, binarization defense evaluated adaptively (BPDA), **gradient masking** (saturated softmax broken by a logit-margin loss) | 7–8 min | ~4 min |
| 2 | [`02_adversarial_text.ipynb`](02_adversarial_text.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/02_adversarial_text.ipynb) | SST-2 sentiment classifier; TextBugger-style typo/homoglyph attack (white-box vs black-box word importance), **universal triggers**, transfer to NB / bigram / char-n-gram models, defenses (char n-grams, **PhantomText** detection & sanitisation + spell-correction, random augmentation — which fails) | 5 min | ~30 s |
| 3 | [`03_backdoor_mnist.ipynb`](03_backdoor_mnist.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/03_backdoor_mnist.ipynb) | BadNets: white-square trigger → class 0; clean accuracy unchanged, ASR ≈ 100%; poison-rate curve (20 samples suffice); **STRIP** run-time detection | 4 min | ~2 min |
| 4 | [`04_membership_inference.ipynb`](04_membership_inference.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/04_membership_inference.ipynb) | Fashion-MNIST overfit MLP; loss-threshold attack, Shokri shadow-model attack, **LiRA** (per-example calibration → real TPR at low FPR); defenses via early stopping / more data | 4 min | ~40 s |

Every notebook opens with a **threat-model table** (goal / knowledge / capability) and closes with take-aways and references, so the
same structure repeats four times: *state the threat model → attack → measure → defend → attack the defense*.

## Setup

**On Google Colab:** click a badge in the table above, then *Runtime → Run all* — the first cell fetches `secai_utils.py`, nothing else to install.

**Locally:**

```bash
pip install -r requirements.txt
jupyter lab
```

`secai_utils.py` (same folder) holds the boilerplate: dataset loaders, two tiny models (`SmallCNN`, `MLP`), `train`/`predict`/`accuracy`
and an image grid plotter. Datasets (MNIST, Fashion-MNIST, SST-2 — ~45 MB total) are downloaded on first use into `data/`;
several mirrors are tried, so it works behind most firewalls. No GPU required; a GPU is used automatically if present.

Notebooks are shipped **with outputs**, so you can show them without re-running. To re-run: *Kernel → Restart & Run All*.
Each notebook is independent — any order works, but 1 → 3 → 4 → 2 (or 1 → 2 → 3 → 4) tells a coherent story.

## Suggested narrative for the 20 minutes

1. **Evasion (NB1).** "The model is wrong, not the human." FGSM → PGD → ε curve. Then the transfer matrix: *secrecy of weights is not a defense*.
   Adversarial training works inside its ε; gradient masking only looks like it works — always evaluate with an adaptive attacker.
2. **Text (NB2).** Same idea, discrete input: the budget is "edits a human won't notice". Homoglyphs are pixel-identical but byte-different.
   Universal triggers → prompt injection. Representation (char n-grams, sanitisation with PhantomText) matters more than the classifier.
3. **Poisoning (NB3).** Training-time attacker; held-out accuracy tells you nothing. A few dozen samples. Supply chain = attack surface. STRIP as a cheap detector.
4. **Privacy (NB4).** Overfitting is a vulnerability. AUC hides the worst case — report TPR at low FPR; LiRA shows why. Only DP gives guarantees.

## Knobs you may want to turn

* Dataset sizes (`load_mnist(n_train=…, n_test=…)`) and epochs — everything is sized for a 2-core CPU; scale up on a GPU.
* NB1 adversarial training: `steps=7`, `epochs=5` on 10k samples; raise for a stronger robust model.
* NB3 trigger: `add_trigger(size=…, value=…)`; try a 2×2 trigger or a blended one to make STRIP struggle.
* NB4: `N_MEMBERS`, `EPOCHS`, `N_SHADOW` — more shadows sharpen LiRA.
