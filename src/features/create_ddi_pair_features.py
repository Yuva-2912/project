import pandas as pd
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path("D:/DDL")

UNIFIED_FEATURES = BASE_DIR / "datasets/final/unified_drug_features.csv"
DDI_MAPPING = BASE_DIR / "datasets/final/ddi_drug_id_mapping.csv"
DDI_PAIRS_IDS = BASE_DIR / "datasets/final/ddi_pairs_with_drug_ids.csv"

OUTPUT = BASE_DIR / "datasets/final/ddi_pair_features.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

unified = pd.read_csv(UNIFIED_FEATURES)
mapping = pd.read_csv(DDI_MAPPING)
ddi = pd.read_csv(DDI_PAIRS_IDS)

print(f"Unified drug features : {unified.shape}")
print(f"Drug ID mapping       : {mapping.shape}")
print(f"DDI pairs with IDs    : {ddi.shape}")


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_unified = ["DrugID"]

required_ddi = [
    "drug_a_ik14",
    "drug_b_ik14",
    "DrugA_ID",
    "DrugB_ID"
]

for col in required_unified:
    if col not in unified.columns:
        raise ValueError(f"Missing column in unified features: {col}")

for col in required_ddi:
    if col not in ddi.columns:
        raise ValueError(f"Missing column in DDI dataset: {col}")


# ============================================================
# PREPARE FEATURE COLUMNS
# ============================================================

# DrugID is the key, not a feature
feature_columns = [
    col for col in unified.columns
    if col != "DrugID"
]

print()
print(f"Number of drug features: {len(feature_columns)}")


# ============================================================
# CREATE DRUG A FEATURES
# ============================================================

print()
print("Merging Drug A features...")

drug_a_features = unified[["DrugID"] + feature_columns].copy()

drug_a_features = drug_a_features.rename(
    columns={
        col: f"A_{col}"
        for col in feature_columns
    }
)

drug_a_features = drug_a_features.rename(
    columns={"DrugID": "DrugA_ID"}
)

ddi = ddi.merge(
    drug_a_features,
    on="DrugA_ID",
    how="left",
    validate="many_to_one"
)

print(f"After Drug A merge: {ddi.shape}")


# ============================================================
# CREATE DRUG B FEATURES
# ============================================================

print()
print("Merging Drug B features...")

drug_b_features = unified[["DrugID"] + feature_columns].copy()

drug_b_features = drug_b_features.rename(
    columns={
        col: f"B_{col}"
        for col in feature_columns
    }
)

drug_b_features = drug_b_features.rename(
    columns={"DrugID": "DrugB_ID"}
)

ddi = ddi.merge(
    drug_b_features,
    on="DrugB_ID",
    how="left",
    validate="many_to_one"
)

print(f"After Drug B merge: {ddi.shape}")


# ============================================================
# MATCHING CHECK
# ============================================================

print()
print("=" * 70)
print("FEATURE MATCHING CHECK")
print("=" * 70)

drug_a_feature_cols = [
    f"A_{col}" for col in feature_columns
]

drug_b_feature_cols = [
    f"B_{col}" for col in feature_columns
]

missing_a = ddi[drug_a_feature_cols].isna().all(axis=1).sum()
missing_b = ddi[drug_b_feature_cols].isna().all(axis=1).sum()

print(f"Pairs without Drug A features: {missing_a}")
print(f"Pairs without Drug B features: {missing_b}")

print(f"Rows before cleaning: {len(ddi)}")


# ============================================================
# REMOVE UNMATCHED ROWS
# ============================================================

ddi = ddi.dropna(
    subset=drug_a_feature_cols + drug_b_feature_cols,
    how="any"
).copy()

print(f"Rows after cleaning : {len(ddi)}")


# ============================================================
# CREATE LABEL
# ============================================================

# RxPairEvid contains observed DDI pairs.
# Therefore these rows represent positive interactions.
if "label" not in ddi.columns:
    ddi["label"] = 1


# ============================================================
# FINAL COLUMN ORGANIZATION
# ============================================================

base_columns = [
    col for col in [
        "drug_a_ik14",
        "drug_b_ik14",
        "a_name",
        "b_name",
        "pair_id",
        "DrugA_ID",
        "DrugB_ID",
        "n_faers_reports",
        "faers_prr_max_strict",
        "faers_ror95_lcl_max_strict",
        "faers_pt_covered_strict",
        "faers_best_pt_code_strict"
    ]
    if col in ddi.columns
]

final_columns = (
    base_columns
    + drug_a_feature_cols
    + drug_b_feature_cols
    + ["label"]
)

ddi = ddi[final_columns]


# ============================================================
# FINAL CHECK
# ============================================================

print()
print("=" * 70)
print("FINAL DDI PAIR FEATURE DATASET")
print("=" * 70)

print(f"Rows    : {len(ddi)}")
print(f"Columns : {len(ddi.columns)}")

print()
print("Label distribution:")
print(ddi["label"].value_counts(dropna=False))

print()
print("Missing values:")
print(
    ddi.isna().sum()
    .loc[lambda x: x > 0]
    .head(20)
)


# ============================================================
# SAVE
# ============================================================

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

ddi.to_csv(
    OUTPUT,
    index=False
)

print()
print("=" * 70)
print("PAIR FEATURE DATASET CREATED")
print("=" * 70)

print(f"Saved: {OUTPUT}")

print()
print("First 5 rows:")
print(ddi.head())