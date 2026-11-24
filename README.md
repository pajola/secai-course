# SecAI — Security of AI: hands-on notebooks

Notebooks for the **SecAI** course. Each one reproduces, from scratch and in a few dozen lines, an attack on machine-learning
systems discussed in class, measures how well it works, and then tests the defenses against it.
The security code is written out by hand (no ART, no TextAttack), so every attack can be read line by line.

**Click a button to run a notebook in Google Colab. Nothing to install.**

## Module 1 — Adversarial Machine Learning

### 1 · Adversarial examples on images &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/01_adversarial_examples_images.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

FGSM and PGD, untargeted vs targeted attacks, **transferability**, adversarial training, gradient masking. An MNIST CNN drops from 98% to 2% accuracy under PGD (ε = 0.2). · [`01_adversarial_examples_images.ipynb`](module-01-adversarial-ml/01_adversarial_examples_images.ipynb)

### 2 · Adversarial examples on text &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/02_adversarial_text.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Typo and homoglyph attacks, **universal triggers**, detection and sanitisation with [PhantomText](https://github.com/lucapajola/PhantomText). Three edits flip 67% of sentiment predictions. · [`02_adversarial_text.ipynb`](module-01-adversarial-ml/02_adversarial_text.ipynb)

### 3 · Backdoors &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/03_backdoor_mnist.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

BadNets data poisoning and **STRIP** detection. At 5% poisoning the backdoor works ≈100% of the time; even 20 poisoned images (0.1% of the data) reach 91%, with no drop in clean accuracy. · [`03_backdoor_mnist.ipynb`](module-01-adversarial-ml/03_backdoor_mnist.ipynb)

### 4 · Membership inference &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-01-adversarial-ml/04_membership_inference.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Loss-threshold, shadow-model and **LiRA** attacks: was this sample in the training set? LiRA finds 10.6% of members at 1% false positives, vs 1.6% for a simple threshold. · [`04_membership_inference.ipynb`](module-01-adversarial-ml/04_membership_inference.ipynb)

Every notebook follows the same structure: **threat model → attack → measure → defend → attack the defense**, and ends with take-aways and the original papers.
The [module README](module-01-adversarial-ml/README.md) has a suggested order for teaching it and the parameters worth changing.

## Module 2 — Data Security for AI

A data risk review of one (synthetic) loan dataset, before it is allowed to train a model. You are the reviewer who signs it off, or blocks it.

### 1 · Inventory and PII discovery &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/01_inventory_and_pii.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

PII hidden in free text (IBANs, health data, ID scans), found by hand and with **Microsoft Presidio**. A **linkage attack** re-identifies 50 of 50 "de-identified" applicants; k-anonymity shows how to stop it. · [`01_inventory_and_pii.ipynb`](module-02-data-security/01_inventory_and_pii.ipynb)

### 2 · Representation and bias audit &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/02_representation_and_bias.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Disparate impact 0.72 on historical decisions. Dropping the gender column doesn't fix it (proxies); mitigations compared with **Fairlearn**. · [`02_representation_and_bias.ipynb`](module-02-data-security/02_representation_and_bias.ipynb)

### 3 · Provenance and integrity &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/03_provenance_and_integrity.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Checksums, **pandera** schema checks and signed manifests. 40 flipped labels (3% of the data) barely change accuracy but make the model approve 89% of weak applications. · [`03_provenance_and_integrity.ipynb`](module-02-data-security/03_provenance_and_integrity.ipynb)

### 4 · The Data Risk Report &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/04_data_risk_report.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Every check in one `audit()`: **BLOCKED**, remediation, then **APPROVED WITH CONDITIONS**, with the report for sign-off. · [`04_data_risk_report.ipynb`](module-02-data-security/04_data_risk_report.ipynb)

The [module README](module-02-data-security/README.md) describes the dataset, the open-source tools used and a suggested teaching order.

## Module 3 — Secure AI Workflow

**Nora**, Northvale's internal RAG chatbot (FastAPI + Ollama + Chroma), hardened one trust boundary at a time. Seven versions run side by side,
from naked (0/8 attacks blocked) to fully hardened (8/8): API gateway, **Llama Prompt Guard 2** on input and on retrieved documents,
permission-aware retrieval, **Presidio** output redaction and a structured audit trail. A paraphrased injection gets past the prompt firewall,
and least privilege stops it anyway: defense in depth.
This module runs locally (Ollama, CPU only), not on Colab. See the [module README](module-03-secure-ai-workflow/README.md) for setup and the recording runbook.

*More modules coming soon.*

## How to run

### Google Colab (recommended)

1. Click an **Open in Colab** button above.
2. *Runtime → Run all*.

The first cell downloads the module's helper file (`secai_utils.py` or `northvale.py`) and installs any tool Colab doesn't have (PhantomText, Presidio, Fairlearn, ...).
A CPU runtime is enough; a GPU is used automatically if you pick one (*Runtime → Change runtime type*).

### On your own machine

```bash
git clone https://github.com/pajola/secai-course.git
cd secai-course/module-01-adversarial-ml      # or module-02-data-security (see its README)
pip install -r requirements.txt
jupyter lab
```

### Good to know

* **Datasets download on first use** (MNIST, Fashion-MNIST, SST-2, about 45 MB) into a `data/` folder next to the notebooks. Several mirrors are tried.
  Module 2 generates its synthetic dataset locally instead.
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
├── module-01-adversarial-ml/
│   ├── README.md                 ← teaching notes and parameters
│   ├── 01_adversarial_examples_images.ipynb
│   ├── 02_adversarial_text.ipynb
│   ├── 03_backdoor_mnist.ipynb
│   ├── 04_membership_inference.ipynb
│   ├── secai_utils.py            ← data loaders, small models, train/eval helpers
│   └── requirements.txt
├── module-02-data-security/
│   ├── README.md                 ← dataset, tools, teaching notes
│   ├── 01_inventory_and_pii.ipynb
│   ├── 02_representation_and_bias.ipynb
│   ├── 03_provenance_and_integrity.ipynb
│   ├── 04_data_risk_report.ipynb
│   ├── northvale.py              ← synthetic dataset generator (seed 42)
│   └── requirements.txt
└── module-03-secure-ai-workflow/
    ├── README.md                 ← setup and recording runbook
    ├── versions/                 ← v0_naked.py … v6_audit.py, one control added per version
    ├── nora/                     ← the controls (gateway, firewall, sanitize, audit) + RAG and LLM
    ├── data/docs/                ← Nora's 5 documents (one is poisoned)
    ├── serve.py                  ← all versions in one server
    ├── attacks.py                ← the 8-attack scoreboard
    ├── pyproject.toml
    └── uv.lock
```

## References

Each notebook ends with the papers it reproduces. The main ones: Goodfellow et al. 2015 (FGSM) · Madry et al. 2018 (PGD, adversarial training) ·
Papernot et al. 2016–17 (transferability) · Athalye, Carlini & Wagner 2018 (obfuscated gradients) · Li et al. 2019 (TextBugger) ·
Wallace et al. 2019 (universal triggers) · Castagnaro et al. 2025 (PhantomText) · Gu et al. 2017 (BadNets) · Gao et al. 2019 (STRIP) ·
Shokri et al. 2017 and Carlini et al. 2022 (membership inference, LiRA) · Sweeney 2002 (k-anonymity) ·
Feldman et al. 2015 (disparate impact) · Agarwal et al. 2018 (fair classification) · Gebru et al. 2021 (datasheets for datasets).

## License

Code: [MIT](LICENSE). Course text and figures: CC BY 4.0. Datasets keep their original licenses (MNIST, Fashion-MNIST, SST-2).

---
*Maintained by Luca Pajola · University of Padova / Spritz Matter.*
