# Module 1 — Adversarial Machine Learning

Four self-contained notebooks on what adversarial attacks are, how they work, how they transfer between models,
and what defenses do (and don't do).

### 1 · Adversarial examples on images &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/01_adversarial_examples_images.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

FGSM and PGD on an MNIST CNN and the accuracy-vs-ε curve · untargeted vs targeted attacks side by side · **transferability matrix** across 3 models · adversarial training · a binarization defense evaluated adaptively (BPDA) · **gradient masking**: a saturated softmax that looks robust until a logit-margin loss breaks it · [`01_adversarial_examples_images.ipynb`](01_adversarial_examples_images.ipynb)

### 2 · Adversarial examples on text &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/02_adversarial_text.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

SST-2 sentiment classifier · TextBugger-style typo and homoglyph attack (white-box vs black-box word importance) · **universal triggers** · transfer to Naive Bayes, bigram and char-n-gram models · defenses: char n-grams, **[PhantomText](https://github.com/lucapajola/PhantomText)** detection and sanitisation + spell-correction, and random augmentation (which fails) · [`02_adversarial_text.ipynb`](02_adversarial_text.ipynb)

### 3 · Backdoors &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/03_backdoor_mnist.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

BadNets: a white-square trigger sends any digit to class 0 · clean accuracy unchanged, attack success ≈ 100% · how much poison is needed (20 samples suffice) · **STRIP** detection at run time · [`03_backdoor_mnist.ipynb`](03_backdoor_mnist.ipynb)

### 4 · Membership inference &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/04_membership_inference.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

An overfit Fashion-MNIST MLP · loss-threshold attack · Shokri shadow-model attack · **LiRA** (per-example calibration, real TPR at low FPR) · defenses: early stopping and more data · [`04_membership_inference.ipynb`](04_membership_inference.ipynb)

Every notebook opens with a **threat-model table** (goal / knowledge / capability) and closes with take-aways and references,
so the same structure repeats four times: *state the threat model → attack → measure → defend → attack the defense*.

## How to run

**On Google Colab:** click a button in the table above, then *Runtime → Run all*. The first cell downloads `secai_utils.py`
(and installs PhantomText in notebook 2); everything else is preinstalled.

**Locally:**

```bash
pip install -r requirements.txt
jupyter lab
```

`secai_utils.py` holds the boilerplate: dataset loaders, two small models (`SmallCNN`, `MLP`), `train` / `predict` / `accuracy`
and an image-grid plotter. Datasets (MNIST, Fashion-MNIST, SST-2, about 45 MB) download on first use into `data/`.
No GPU required; one is used automatically if present.

Notebooks are saved **with their outputs**, so they can be shown without re-running. To re-run: *Kernel → Restart & Run All*.

## Suggested order for teaching

Each notebook is independent, so any order works. 1 → 2 → 3 → 4 tells a coherent story:

1. **Evasion (NB1).** "The model is wrong, not the human." FGSM → PGD → ε curve. Untargeted vs targeted: making the model fail vs choosing what it says.
   Then the transfer matrix: *secrecy of weights is not a defense*. Adversarial training works inside its ε; gradient masking only looks like it works — always evaluate with an adaptive attacker.
2. **Text (NB2).** Same idea, discrete input: the budget is "edits a human won't notice". Homoglyphs look identical but are different bytes.
   Universal triggers are the ancestor of prompt injection. Fixing the representation (char n-grams, sanitisation with PhantomText) matters more than the classifier — and a sanitiser is only as good as its character tables.
3. **Poisoning (NB3).** A training-time attacker; held-out accuracy tells you nothing. A few dozen samples are enough. The supply chain is the attack surface. STRIP as a cheap detector.
4. **Privacy (NB4).** Overfitting is a vulnerability. AUC hides the worst case — report TPR at low FPR; LiRA shows why. Only differential privacy gives guarantees.

## Parameters worth changing

* Dataset sizes (`load_mnist(n_train=…, n_test=…)`) and epochs — kept small so everything runs on a CPU; scale up on a GPU.
* NB1 adversarial training: `steps=7`, `epochs=5` on 10k samples; raise them for a stronger robust model.
* NB1 targeted attack: change `TARGET`, or lower ε to see targeted attacks fail before untargeted ones do.
* NB2: `max_edits` in the attack; add a zero-width or diacritical "bug" and see whether PhantomText catches it.
* NB3 trigger: `add_trigger(size=…, value=…)`; try a 2×2 trigger or a blended one to make STRIP struggle.
* NB4: `N_MEMBERS`, `EPOCHS`, `N_SHADOW` — more shadow models sharpen LiRA.
