# SecAI — Security of AI: hands-on notebooks

Demonstrative Jupyter notebooks accompanying the **SecAI** course. Each module is a self-contained folder of short notebooks
(a few minutes of live walkthrough each) that reproduce, from scratch and in a few dozen lines, the attacks and defenses discussed in class.
The code is deliberately library-free on the security side (no ART / TextAttack): every attack is written out so you can read it.

## Modules

| # | Module | Status | Contents |
|---|---|---|---|
| 1 | [`module-01-adversarial-ml/`](module-01-adversarial-ml/) | ✅ available | Adversarial examples on images and text, transferability, backdoors, membership inference, and the defenses that (don't) work |
| 2 | *coming soon* | 🚧 | |
| 3 | *coming soon* | 🚧 | |

Every notebook follows the same structure — **threat model → attack → measure → defend → attack the defense** — and ends with take-aways and references to the original papers.

### Module 1 — Adversarial Machine Learning (~20 min live)

| Notebook | Run | Topic | Key results |
|---|---|---|---|
| [`01_adversarial_examples_images.ipynb`](module-01-adversarial-ml/01_adversarial_examples_images.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/01_adversarial_examples_images.ipynb) | FGSM, PGD, targeted attacks, **transferability**, adversarial training, gradient masking (BPDA, logit-margin loss) | MNIST CNN 98% → 2% under PGD (ε=0.2); black-box transfer drops accuracy to 0.3–0.6; adversarial training recovers ~80% |
| [`02_adversarial_text.ipynb`](module-01-adversarial-ml/02_adversarial_text.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/02_adversarial_text.ipynb) | Typo / homoglyph attacks, black-box word importance, **universal triggers**, transfer, input normalisation | 3 edits flip 67% of sentiment predictions; a 3-word trigger flips 96%; normalisation cuts attack success to 16% |
| [`03_backdoor_mnist.ipynb`](module-01-adversarial-ml/03_backdoor_mnist.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/03_backdoor_mnist.ipynb) | BadNets data poisoning, poison-rate curve, **STRIP** run-time detection | 20 poisoned samples (0.1%) → 91% attack success with unchanged clean accuracy; STRIP detects 99% at 1% FPR |
| [`04_membership_inference.ipynb`](module-01-adversarial-ml/04_membership_inference.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/04_membership_inference.ipynb) | Loss-threshold, shadow-model and **LiRA** attacks; TPR at low FPR; early stopping / more data as defenses | LiRA: 10.6% TPR at 1% FPR vs 1.6% for a global threshold |

See the [module README](module-01-adversarial-ml/README.md) for the suggested narrative, timings and knobs to turn.

## Getting started

### Option A — Google Colab (nothing to install)

Click any **Open in Colab** badge above. The first code cell downloads the helper module `secai_utils.py`;
then run everything with *Runtime → Run all*. All other dependencies are preinstalled on Colab, and a CPU runtime is enough.

### Option B — locally

```bash
git clone https://github.com/pajola/secai-course.git
cd secai-course/module-01-adversarial-ml
pip install -r requirements.txt
jupyter lab
```

* **No GPU needed.** Everything is sized for a laptop CPU (the whole module runs in under 10 minutes); a GPU is used automatically if present.
* **Datasets download on first use** (MNIST, Fashion-MNIST, SST-2 — ~45 MB) into a local `data/` folder, which is git-ignored. Several mirrors are tried, so it works behind most firewalls.
* Notebooks are committed **with outputs**, so they can be read on GitHub or shown in class without re-running. To regenerate: *Kernel → Restart & Run All*.
* Each module has its own `requirements.txt`; the only shared helper is the module-local `secai_utils.py` (data loaders, tiny models, train/eval loops).

## Repository layout

```
secai-course/
├── README.md                      ← this file
├── LICENSE
├── module-01-adversarial-ml/
│   ├── README.md                  ← narrative, timings, knobs
│   ├── 01_adversarial_examples_images.ipynb
│   ├── 02_adversarial_text.ipynb
│   ├── 03_backdoor_mnist.ipynb
│   ├── 04_membership_inference.ipynb
│   ├── secai_utils.py
│   └── requirements.txt
└── module-02-.../                 ← coming soon
```

## For students

The notebooks are meant to be *modified*: change the ε budget, the trigger, the number of shadow models, the dataset size — every
notebook's README lists the knobs. If a result surprises you (why does binarization hold on MNIST? why does random augmentation
not help against typos?), that is the point: the text explains what the number means and what it does **not** mean.

## References

Each notebook closes with the papers it reproduces. The main ones: Goodfellow et al. 2015 (FGSM) · Madry et al. 2018 (PGD, adversarial training) ·
Papernot et al. 2016–17 (transferability) · Athalye, Carlini & Wagner 2018 (obfuscated gradients) · Li et al. 2019 (TextBugger) ·
Wallace et al. 2019 (universal triggers) · Gu et al. 2017 (BadNets) · Gao et al. 2019 (STRIP) · Shokri et al. 2017 and Carlini et al. 2022 (membership inference, LiRA).

## License

Code: MIT. Course text and figures: CC BY 4.0. Datasets keep their original licenses (MNIST, Fashion-MNIST, SST-2).

---
*Maintained by Luca Pajola · University of Padova / Spritz Matter.*
