import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path("D:/DDL")

UNIFIED_FEATURES = BASE_DIR / "datasets/final/unified_drug_features.csv"
DDI_MAPPING = BASE_DIR / "datasets/final/ddi_drug_id_mapping.csv"
DDI_PAIRS_IDS = BASE_DIR / "datasets/final/ddi_pairs_with_drug_ids.csv"

OUTPUT = BASE_DIR / "datasets/final/ddi_training_dataset.csv"


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

unified = pd.read_csv(UNIFIED_FEATURES)
mapping = pd.read_csv(DDI_MAPPING)
ddi = pd.read_csv(DDI_PAIRS_IDS)

print(f"Unified features : {unified.shape}")
print(f"DDI pairs        : {ddi.shape}")


# ============================================================
# PREPARE DRUG FEATURES
# ============================================================

# Remove identifiers/text from ML features
excluded_columns = [
    "DrugID",
    "DrugName"
]

feature_columns = [
    col for col in unified.columns
    if col not in excluded_columns
]

print()
print(f"ML drug features: {len(feature_columns)}")


# ============================================================
# NUMERIC FEATURE CONVERSION
# ============================================================

for col in feature_columns:
    unified[col] = pd.to_numeric(
        unified[col],
        errors="coerce"
    )


# ============================================================
# IMPUTE MISSING VALUES
# ============================================================

print()
print("=" * 70)
print("IMPUTING MISSING VALUES")
print("=" * 70)

missing_before = unified[feature_columns].isna().sum().sum()

print(f"Missing feature values before: {missing_before}")

# Median imputation
for col in feature_columns:
    median_value = unified[col].median()

    if pd.isna(median_value):
        median_value = 0.0

    unified[col] = unified[col].fillna(median_value)

missing_after = unified[feature_columns].isna().sum().sum()

print(f"Missing feature values after : {missing_after}")


# ============================================================
# DRUG A FEATURES
# ============================================================

drug_a = unified[
    ["DrugID"] + feature_columns
].copy()

drug_a = drug_a.rename(
    columns={
        "DrugID": "DrugA_ID",
        **{
            col: f"A_{col}"
            for col in feature_columns
        }
    }
)


# ============================================================
# DRUG B FEATURES
# ============================================================

drug_b = unified[
    ["DrugID"] + feature_columns
].copy()

drug_b = drug_b.rename(
    columns={
        "DrugID": "DrugB_ID",
        **{
            col: f"B_{col}"
            for col in feature_columns
        }
    }
)


# ============================================================
# MERGE POSITIVE PAIRS
# ============================================================

print()
print("=" * 70)
print("CREATING POSITIVE PAIRS")
print("=" * 70)

positive = ddi[
    ["drug_a_ik14", "drug_b_ik14",
     "a_name", "b_name",
     "pair_id",
     "DrugA_ID", "DrugB_ID"]
].copy()

positive = positive.merge(
    drug_a,
    on="DrugA_ID",
    how="inner",
    validate="many_to_one"
)

positive = positive.merge(
    drug_b,
    on="DrugB_ID",
    how="inner",
    validate="many_to_one"
)

positive["label"] = 1

print(f"Positive pairs: {len(positive)}")


# ============================================================
# CREATE SET OF EXISTING DDI PAIRS
# ============================================================

positive_keys = set(
    zip(
        positive["DrugA_ID"].astype(int),
        positive["DrugB_ID"].astype(int)
    )
)

# Treat DDI as undirected:
# (A,B) == (B,A)

positive_undirected = {
    tuple(sorted((a, b)))
    for a, b in positive_keys
}


# ============================================================
# GENERATE NEGATIVE PAIRS
# ============================================================

print()
print("=" * 70)
print("GENERATING NEGATIVE PAIRS")
print("=" * 70)

rng = np.random.default_rng(42)

drug_ids = unified["DrugID"].astype(int).tolist()

target_negative_count = len(positive)

negative_pairs = set()

while len(negative_pairs) < target_negative_count:

    a = int(rng.choice(drug_ids))
    b = int(rng.choice(drug_ids))

    # No self-interaction
    if a == b:
        continue

    pair = tuple(sorted((a, b)))

    # Must not already be a known DDI
    if pair in positive_undirected:
        continue

    negative_pairs.add(pair)


print(f"Negative pairs: {len(negative_pairs)}")


# ============================================================
# CREATE NEGATIVE DATAFRAME
# ============================================================

negative = pd.DataFrame(
    list(negative_pairs),
    columns=["DrugA_ID", "DrugB_ID"]
)

negative["label"] = 0

negative = negative.merge(
    drug_a,
    on="DrugA_ID",
    how="inner"
)

negative = negative.merge(
    drug_b,
    on="DrugB_ID",
    how="inner"
)


# ============================================================
# COMBINE POSITIVE + NEGATIVE
# ============================================================

print()
print("=" * 70)
print("COMBINING DATASET")
print("=" * 70)

# Keep only ML-relevant columns
positive_model = positive[
    ["DrugA_ID", "DrugB_ID"]
    + [f"A_{c}" for c in feature_columns]
    + [f"B_{c}" for c in feature_columns]
    + ["label"]
].copy()

negative_model = negative[
    ["DrugA_ID", "DrugB_ID"]
    + [f"A_{c}" for c in feature_columns]
    + [f"B_{c}" for c in feature_columns]
    + ["label"]
].copy()

dataset = pd.concat(
    [positive_model, negative_model],
    ignore_index=True
)


# ============================================================
# SHUFFLE
# ============================================================

dataset = dataset.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# FINAL CHECKS
# ============================================================

print()
print("=" * 70)
print("FINAL TRAINING DATASET")
print("=" * 70)

print(f"Rows    : {len(dataset)}")
print(f"Columns : {len(dataset.columns)}")

print()
print("Label distribution:")
print(dataset["label"].value_counts())

print()
print("Missing values:")
print(
    dataset.isna().sum().sum()
)

print()
print("Positive : Negative")
print(
    len(dataset[dataset["label"] == 1]),
    ":",
    len(dataset[dataset["label"] == 0])
)


# ============================================================
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

dataset.to_csv(
    OUTPUT,
    index=False
)

print()
print("=" * 70)
print("TRAINING DATASET CREATED")
print("=" * 70)

print(f"Saved: {OUTPUT}")