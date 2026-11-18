"""
Northvale Lending (fictional) — synthetic dataset for the SecAI data-security module.

Everything here is invented: the company, the people, the IBANs, the notes. The generator is
deterministic (seed 42), so every notebook, slide and student sees exactly the same numbers.

    from northvale import load, reexport_from_source, batch_sha256
    df, manifest = load()          # writes data/northvale/*.csv on first use

The dataset is built to contain the problems a data-risk review should find:
  * direct identifiers (name, email, phone, date of birth) and PII hidden in free text
    (IBANs, health information, ID-document scans, co-signer names);
  * an imbalanced population (gender, applicants aged 60+);
  * historical bias in the labels, partly carried by a proxy (postcode, income);
  * one ingestion batch whose content no longer matches its recorded checksum, and one
    batch bought from a broker with no owner, no legal basis and no checksum.
"""
import hashlib, os
import numpy as np
import pandas as pd

SEED = 42
REF_DATE = pd.Timestamp("2025-06-30")      # date of the export; ages are computed at this date
COLUMNS = ["applicant_id", "full_name", "email", "phone", "date_of_birth", "gender", "postcode",
           "annual_income_eur", "credit_score", "loan_amount_eur", "advisor_notes", "source_batch", "approved"]

# postcode: (rows, women, approved men, approved women, wealth factor)
# The approval counts encode past human decisions (historical bias); the wealth factor shifts income.
POSTCODES = {
    "35121": (150, 35, 82, 20, 1.15),
    "35122": (100, 20, 66, 12, 1.35),
    "35123": (150, 40, 75, 22, 1.05),
    "35124": (150, 45, 66, 22, 0.95),
    "35125": (150, 40, 70, 21, 1.00),
    "35131": (150, 50, 60, 22, 0.90),
    "35135": (150, 48, 61, 20, 0.88),
    "35136": (200, 90, 55, 32, 0.80),
}
BATCHES = {"B1_core_banking": 528, "B2_core_banking": 414, "B3_broker_purchase": 258}
N_SENIOR = 44              # applicants aged 60+
N_TAMPERED = 40            # B2 rows whose label was flipped (rejected -> approved) after export
N_IBAN, N_IBAN_DECOY, N_HEALTH, N_IDDOC, N_COSIGNER = 110, 18, 97, 86, 60

MANIFEST = [
    dict(batch_id="B1_core_banking", origin="Core banking export, applications 2022-2023", owner="Credit Risk Office",
         legal_basis="GDPR Art. 6(1)(b) contract; DPIA-2024-07", license="internal"),
    dict(batch_id="B2_core_banking", origin="Core banking export, applications 2024", owner="Credit Risk Office",
         legal_basis="GDPR Art. 6(1)(b) contract; DPIA-2024-07", license="internal"),
    dict(batch_id="B3_broker_purchase", origin="Lead list bought from a broker (LeadMax s.r.l., fictional)", owner="",
         legal_basis="", license=""),
]

HEALTH_NOTES = [
    "Recent hospital stay after cardiac surgery, back at work since March.",
    "Was on sick leave for three months last year (back injury).",
    "Mentions ongoing chemotherapy, says income is not affected.",
    "Diabetic, regular check-ups, no impact on job.",
    "Hospitalised in 2023 after a car accident, fully recovered.",
    "Pregnant, maternity leave expected in the autumn.",
    "Takes medication for depression, says it is under control.",
]
IDDOC_NOTES = [
    "Copy of ID card scanned and attached to the file.",
    "Passport scan saved in the shared folder.",
    "Photo of driving licence received by WhatsApp.",
]
BASE_NOTES = [
    "Stable employment, {y} years at current employer.",
    "Self-employed, income documented via tax returns.",
    "Permanent contract, public sector.",
    "Fixed-term contract, renewal expected.",
    "Wants to consolidate two existing loans.",
    "Loan for car purchase, quote attached.",
    "Loan for home renovation, contractor estimate provided.",
    "Existing customer, no missed payments.",
    "First-time customer, referred by a branch colleague.",
]


def _iban_checksum_ok(iban):
    s = iban.replace(" ", "")
    s = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in s)) % 97 == 1


def _spaced(iban):
    return " ".join(iban[i:i + 4] for i in range(0, len(iban), 4))


def _generate():
    from faker import Faker
    rng = np.random.default_rng(SEED)
    fake = Faker("it_IT"); fake.seed_instance(SEED)

    # --- population: postcode x gender cells ------------------------------------------------
    rows = []
    for pc, (n, n_f, a_m, a_f, wealth) in POSTCODES.items():
        rows += [dict(postcode=pc, gender="F", wealth=wealth)] * n_f
        rows += [dict(postcode=pc, gender="M", wealth=wealth)] * (n - n_f)
    df = pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)
    n = len(df)

    ages = np.concatenate([rng.integers(22, 60, n - N_SENIOR), rng.integers(60, 73, N_SENIOR)])
    rng.shuffle(ages)
    df["date_of_birth"] = [(REF_DATE - pd.DateOffset(years=int(a)) - pd.Timedelta(days=int(rng.integers(1, 365)))).date().isoformat()
                           for a in ages]

    pay_gap = np.where(df.gender == "F", 0.85, 1.0)
    df["annual_income_eur"] = (rng.lognormal(np.log(32_000), 0.35, n) * df.wealth * pay_gap / 100).round() * 100
    df["credit_score"] = np.clip(rng.normal(690, 60, n) + (np.log(df.annual_income_eur) - np.log(32_000)) * 60, 300, 850).round().astype(int)
    df["loan_amount_eur"] = (df.annual_income_eur * rng.uniform(0.2, 1.0, n) / 500).round().clip(2) * 500

    # --- batches ----------------------------------------------------------------------------
    df["source_batch"] = np.repeat(list(BATCHES), list(BATCHES.values()))[rng.permutation(n)]

    # --- the tampered rows: weak applications in B2 that someone marked "approved" ------------
    b2 = np.flatnonzero(df.source_batch == "B2_core_banking")
    tampered = rng.choice(b2, N_TAMPERED, replace=False)
    df.loc[tampered, "credit_score"] = rng.integers(470, 560, N_TAMPERED)
    df.loc[tampered, "loan_amount_eur"] = (df.loc[tampered, "annual_income_eur"] * rng.uniform(0.9, 1.3, N_TAMPERED) / 500).round() * 500
    df["_tampered"] = False; df.loc[tampered, "_tampered"] = True

    # --- labels: within each postcode x gender cell, approve the strongest applications until
    #     the historical quota is met (tampered rows are approved regardless) -----------------
    merit = ((df.credit_score - 690) / 60 + np.log(df.annual_income_eur / 32_000) * 2
             - df.loan_amount_eur / df.annual_income_eur * 1.5 + rng.normal(0, 0.6, n))
    df["approved"] = 0
    for pc, (n_pc, n_f, a_m, a_f, _) in POSTCODES.items():
        for g, quota in (("M", a_m), ("F", a_f)):
            cell = df[(df.postcode == pc) & (df.gender == g)]
            forced = cell.index[cell._tampered]
            rest = merit[cell.index[~cell._tampered]].sort_values(ascending=False)
            df.loc[forced, "approved"] = 1
            df.loc[rest.index[:quota - len(forced)], "approved"] = 1

    # --- identities ---------------------------------------------------------------------------
    names, emails, phones = [], [], []
    for g in df.gender:
        first = fake.first_name_female() if g == "F" else fake.first_name_male()
        last = fake.last_name()
        names.append(f"{first} {last}")
        user = f"{first}.{last}".lower().replace(" ", "").replace("'", "")
        emails.append(f"{user}{rng.integers(1, 99)}@{fake.free_email_domain()}")
        phones.append(fake.phone_number())
    df["full_name"], df["email"], df["phone"] = names, emails, phones
    df["applicant_id"] = [f"NV-{i:05d}" for i in rng.permutation(np.arange(10_001, 10_001 + n))]

    # --- free-text advisor notes, with PII hidden in some of them --------------------------------
    notes = [[BASE_NOTES[i].format(y=rng.integers(2, 25))] for i in rng.integers(0, len(BASE_NOTES), n)]
    def pick(k): return rng.choice(n, k, replace=False)
    for i in pick(N_IBAN):
        iban = fake.iban()
        notes[i].append(f"Salary credited to IBAN {_spaced(iban) if rng.random() < 0.5 else iban}.")
    for i in pick(N_IBAN_DECOY):                  # IBAN-shaped strings with a wrong check digit
        iban = list(fake.iban()); iban[-1] = str((int(iban[-1]) + 1) % 10); iban = "".join(iban)
        assert not _iban_checksum_ok(iban)
        notes[i].append(f"Old account number on file: {iban} (typo? to be verified).")
    for i in pick(N_HEALTH):
        notes[i].append(HEALTH_NOTES[rng.integers(len(HEALTH_NOTES))])
    for i in pick(N_IDDOC):
        notes[i].append(IDDOC_NOTES[rng.integers(len(IDDOC_NOTES))])
    for i in pick(N_COSIGNER):
        notes[i].append(f"Co-signer: {fake.name()}, spouse.")
    df["advisor_notes"] = [" ".join(x) for x in notes]

    source_b2 = df[df.source_batch == "B2_core_banking"].copy()
    source_b2.loc[source_b2._tampered, "approved"] = 0       # what the core banking system really says
    return df[COLUMNS], source_b2[COLUMNS]


_CACHE = {}
def _data():
    if not _CACHE:
        _CACHE["delivered"], _CACHE["source_b2"] = _generate()
    return _CACHE["delivered"], _CACHE["source_b2"]


def batch_sha256(batch_df):
    """SHA-256 of a batch in a canonical form: fixed column order, sorted by applicant_id, CSV."""
    canon = batch_df[COLUMNS].sort_values("applicant_id").to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def reexport_from_source(batch_id):
    """Ask the source system for a fresh copy of a batch (only the core-banking batches have a source)."""
    delivered, source_b2 = _data()
    if batch_id == "B2_core_banking":
        return source_b2.reset_index(drop=True)
    if batch_id == "B1_core_banking":
        return delivered[delivered.source_batch == batch_id].reset_index(drop=True)
    raise ValueError(f"{batch_id}: no source system to re-export from")


def load(data_dir="data/northvale"):
    """Return (loans, manifest). Writes the two CSV files on first use, then reads them back."""
    loans_csv = os.path.join(data_dir, "northvale_loans.csv")
    manifest_csv = os.path.join(data_dir, "provenance_manifest.csv")
    if not (os.path.exists(loans_csv) and os.path.exists(manifest_csv)):
        os.makedirs(data_dir, exist_ok=True)
        delivered, source_b2 = _data()
        delivered.to_csv(loans_csv, index=False)
        rows = []
        for m in MANIFEST:
            # the checksum was recorded when each batch left its source system
            src = {"B1_core_banking": delivered[delivered.source_batch == "B1_core_banking"],
                   "B2_core_banking": source_b2}.get(m["batch_id"])
            rows.append(dict(m, rows=BATCHES[m["batch_id"]], sha256=batch_sha256(src) if src is not None else ""))
        pd.DataFrame(rows).to_csv(manifest_csv, index=False)
    dtypes = {"postcode": str, "phone": str}
    loans = pd.read_csv(loans_csv, dtype=dtypes)
    manifest = pd.read_csv(manifest_csv, dtype=str, keep_default_na=False)
    return loans, manifest
