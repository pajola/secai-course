# SecAI — Security of AI: hands-on notebooks

Notebooks for the **SecAI** course. Each one reproduces, from scratch and in a few dozen lines, an attack on machine-learning
systems discussed in class, measures how well it works, and then tests the defenses against it.
The security code is written out by hand (no ART, no TextAttack), so every attack can be read line by line.

**Click a button to run a notebook in Google Colab. Nothing to install.**

## Module 1 — Adversarial Machine Learning

### 1 · Adversarial examples on images

<a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/01_adversarial_examples_images.ipynb"><img src="https://img.shields.io/badge/Open%20in%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white" alt="Open in Colab" width="260"></a>

FGSM and PGD, untargeted vs targeted attacks, **transferability**, adversarial training, gradient masking. An MNIST CNN drops from 98% to 2% accuracy under PGD (ε = 0.2). · [`01_adversarial_examples_images.ipynb`](module-01-adversarial-ml/01_adversarial_examples_images.ipynb)

### 2 · Adversarial examples on text

<a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/02_adversarial_text.ipynb"><img src="https://img.shields.io/badge/Open%20in%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white" alt="Open in Colab" width="260"></a>

Typo and homoglyph attacks, **universal triggers**, detection and sanitisation with [PhantomText](https://github.com/lucapajola/PhantomText). Three edits flip 67% of sentiment predictions. · [`02_adversarial_text.ipynb`](module-01-adversarial-ml/02_adversarial_text.ipynb)

### 3 · Backdoors

<a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/03_backdoor_mnist.ipynb"><img src="https://img.shields.io/badge/Open%20in%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white" alt="Open in Colab" width="260"></a>

BadNets data poisoning and **STRIP** detection. 20 poisoned images (0.1% of the data) plant a backdoor that works 91% of the time, with no drop in clean accuracy. · [`03_backdoor_mnist.ipynb`](module-01-adversarial-ml/03_backdoor_mnist.ipynb)

### 4 · Membership inference

<a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/04_membership_inference.ipynb"><img src="https://img.shields.io/badge/Open%20in%20Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white" alt="Open in Colab" width="260"></a>

Loss-threshold, shadow-model and **LiRA** attacks: was this sample in the training set? LiRA finds 10.6% of members at 1% false positives, vs 1.6% for a simple threshold. · [`04_membership_inference.ipynb`](module-01-adversarial-ml/04_membership_inference.ipynb)

Every notebook follows the same structure: **threat model → attack → measure → defend → attack the defense**, and ends with take-aways and the original papers.
The [module README](module-01-adversarial-ml/README.md) has a suggested order for teaching it and the parameters worth changing.

*More modules coming soon.*

## How to run

### Google Colab (recommended)

1. Click an **Open in Colab** button above.
2. *Runtime → Run all*.

The first cell downloads the helper file `secai_utils.py` (and, for notebook 2, installs PhantomText). The rest is preinstalled on Colab.
A CPU runtime is enough; a GPU is used automatically if you pick one (*Runtime → Change runtime type*).

### On your own machine

```bash
git clone https://github.com/pajola/secai-course.git
cd secai-course/module-01-adversarial-ml
pip install -r requirements.txt
jupyter lab
```

### Good to know

* **Datasets download on first use** (MNIST, Fashion-MNIST, SST-2, about 45 MB) into a `data/` folder next to the notebooks. Several mirrors are tried.
* **Notebooks are saved with their outputs**, so you can read the results on GitHub without running anything.
* **No GPU required.** Every experiment is sized to run on a normal laptop.

## For students

The notebooks are meant to be *changed*: try a different ε, a different trigger, more shadow models, a bigger dataset — the
[module README](module-01-adversarial-ml/README.md#parameters-worth-changing) lists the parameters worth playing with.
If a result surprises you (why does binarization hold on MNIST? why does random augmentation not help against typos?), that is the point:
the text explains what each number means, and what it does **not** mean.

## Repository layout

```
secai-course/
├── README.md
├── LICENSE
└── module-01-adversarial-ml/
    ├── README.md                 ← teaching notes and parameters
    ├── 01_adversarial_examples_images.ipynb
    ├── 02_adversarial_text.ipynb
    ├── 03_backdoor_mnist.ipynb
    ├── 04_membership_inference.ipynb
    ├── secai_utils.py            ← data loaders, small models, train/eval helpers
    └── requirements.txt
```

## References

Each notebook ends with the papers it reproduces. The main ones: Goodfellow et al. 2015 (FGSM) · Madry et al. 2018 (PGD, adversarial training) ·
Papernot et al. 2016–17 (transferability) · Athalye, Carlini & Wagner 2018 (obfuscated gradients) · Li et al. 2019 (TextBugger) ·
Wallace et al. 2019 (universal triggers) · Castagnaro et al. 2025 (PhantomText) · Gu et al. 2017 (BadNets) · Gao et al. 2019 (STRIP) ·
Shokri et al. 2017 and Carlini et al. 2022 (membership inference, LiRA).

## License

Code: [MIT](LICENSE). Course text and figures: CC BY 4.0. Datasets keep their original licenses (MNIST, Fashion-MNIST, SST-2).

---
*Maintained by Luca Pajola · University of Padova / Spritz Matter.*
