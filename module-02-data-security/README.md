# Module 2 — Data Security for AI

A data risk review of one dataset, in four notebooks. **Northvale Lending** (fictional) wants to train a loan-approval model on 1,200 historical
applications. Before anything reaches a training pipeline, the AI security team reviews the data. The learner is the reviewer who signs off on the dataset, or blocks it.

### 1 · Inventory and PII discovery &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/01_inventory_and_pii.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Column inventory and pattern scan · PII hidden in free text: IBANs validated with mod-97, health data (GDPR Art. 9), ID-document scans, third-party names ·
the same job with **Microsoft Presidio**, including what it misses and custom recognisers · classification and minimisation ·
**linkage attack**: 50 of 50 "de-identified" applicants re-identified, then k-anonymity and l-diversity · [`01_inventory_and_pii.ipynb`](01_inventory_and_pii.ipynb)

### 2 · Representation and bias audit &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/02_representation_and_bias.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Label balance vs population balance · confidence intervals for small groups · disparate impact ratio 0.72 and the four-fifths rule, by hand and with **Fairlearn** ·
**fairness through unawareness fails**: a model without the gender column is still biased (historical labels + postcode/income proxies) ·
mitigations compared: reweighing, a fairness constraint, per-group thresholds · [`02_representation_and_bias.ipynb`](02_representation_and_bias.ipynb)

### 3 · Provenance and integrity &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/03_provenance_and_integrity.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

Provenance manifest and SHA-256 checks · schema and business-rule checks with **pandera** · re-export from the source to find the 40 flipped labels ·
**a 3% label flip barely changes accuracy but makes the model approve 89% of weak applications** · the manifest as an attack surface, fixed with Ed25519 signatures · [`03_provenance_and_integrity.ipynb`](03_provenance_and_integrity.ipynb)

### 4 · The Data Risk Report &nbsp; <a href="https://colab.research.google.com/github/pajola/secai-course/blob/main/module-02-data-security/04_data_risk_report.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" width="150" align="center"></a>

All checks in one `audit()` · decision **BLOCKED** · remediation · second run: **APPROVED WITH CONDITIONS** · the report for data owner, AI security and DPO sign-off ·
optional comparison with a generic profiler (**ydata-profiling**) · [`04_data_risk_report.ipynb`](04_data_risk_report.ipynb)

Notebook 4 follows the six steps of the review in order and runs on its own, so it also works as a short live demo.

## The dataset

All data is synthetic and invented: company, people, IBANs, notes. [`northvale.py`](northvale.py) generates it deterministically (seed 42) on first use, into `data/northvale/`:

* `northvale_loans.csv`: 1,200 rows, 13 columns (`applicant_id, full_name, email, phone, date_of_birth, gender, postcode, annual_income_eur, credit_score, loan_amount_eur, advisor_notes, source_batch, approved`)
* `provenance_manifest.csv`: 3 ingestion batches with origin, owner, legal basis, license and checksum

It is built to contain what the review should find:

| Step | Finding |
|---|---|
| PII in free text | valid IBAN in 110 rows (9.2%), health mentions in 97 (8.1%), ID-document scans in 86 (7.2%) |
| Representation | label 58.8% / 41.2% · gender 69.3% M / 30.7% F · aged 60+: 3.7% |
| Bias | approval M 64.3% vs F 46.5% → DI 0.72 · by postcode 43.5% (35136) to 78.0% (35122) |
| Provenance | B1 (528 rows) clean · B2 (414) checksum mismatch: 40 labels flipped · B3 (258) bought from a broker, no owner, legal basis or checksum |

## How to run

**On Google Colab:** click a button above, then *Runtime → Run all*. The first cell downloads `northvale.py` and installs the tools each notebook needs (about a minute for notebook 1, which also fetches a small spaCy model).

**Locally:**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
jupyter lab
```

No GPU needed; every notebook runs in under a minute on a laptop. Notebooks are saved **with their outputs**.

## Open-source tools

Each check is first written by hand, then compared with a widely used tool:

| Tool | Used for | Notebook |
|---|---|---|
| [Faker](https://faker.readthedocs.io) | synthetic identities | dataset |
| [Microsoft Presidio](https://microsoft.github.io/presidio/) | PII detection and redaction | 1 |
| [python-stdnum](https://arthurdejong.org/python-stdnum/) | IBAN validation | 1 |
| [Fairlearn](https://fairlearn.org) | group metrics, fairness-constrained training | 2 |
| [pandera](https://pandera.readthedocs.io) | schema and data-quality checks | 3 |
| [cryptography](https://cryptography.io) | Ed25519 manifest signatures | 3 |
| [ydata-profiling](https://github.com/ydataai/ydata-profiling) | dataset profile (optional) | 4 |

## Suggested order for teaching

1. **Inventory and PII (NB1).** "You can't protect what you haven't inventoried." The structured PII is obvious; the finding is the free text. Tools miss what nobody wrote a rule for (health). Removing names is not anonymisation: linkage attack, then k-anonymity.
2. **Bias (NB2).** "A balanced label does not mean a balanced population." DI 0.72 on the labels; dropping the gender column doesn't help (Amazon recruiting tool). Mitigations trade accuracy for parity, and accuracy is measured against biased labels.
3. **Provenance (NB3).** Schema checks catch broken data; integrity checks catch changed data. The poisoned model has the same accuracy (module 1, NB3). A hash next to the data protects nothing: sign the manifest.
4. **Report (NB4).** One decision, three signatures. The review as code, so it runs before every training job.

> *A dataset is an attack surface, a liability, and a decision record, all at once. Review it before it becomes a model.*

## Parameters worth changing

* NB1: add your own Presidio recogniser (e.g. Italian tax codes, `codice fiscale`); change the age bands and watch k change.
* NB2: `DemographicParity(ratio_bound=…)`; try `EqualizedOdds` instead; add postcode-free features and re-run the proxy detector.
* NB3: in `northvale.py`, change `N_TAMPERED` (how few flipped labels still change the model?) or make the attacker respect the credit policy (scores ≥ 560) and see which check still catches it.
* NB4: tighten the thresholds in `audit()` (k ≥ 10, each gender ≥ 45%) and see which findings change status.
