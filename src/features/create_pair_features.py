# scripts/features/create_pair_features.py

import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

DRUG_FEATURES_FILE = "datasets/final/unified_drug_features.csv"
DDI_PAIRS_FILE = "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"
OUTPUT_FILE = "datasets/final/ddi_pair_features.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

drug_features = pd.read_csv(DRUG_FEATURES_FILE)
ddi_pairs = pd.read_csv(DDI_PAIRS_FILE)

print(f"Drug feature shape : {drug_features.shape}")
print(f"DDI pair shape     : {ddi_pairs.shape}")


# ============================================================
# IDENTIFY DRUG ID COLUMN
# ============================================================

possible_id_columns = [
    "DrugID",
    "drug_id",
    "Drug_Id",
    "drugid",
    "drug_a_ik14"
]

drug_id_column = None

for col in possible_id_columns:
    if col in drug_features.columns:
        drug_id_column = col
        break

if drug_id_column is None:
    raise ValueError(
        "Drug ID column not found in unified_drug_features.csv"
    )

print(f"Drug ID column: {drug_id_column}")


# ============================================================
# IDENTIFY DDI PAIR COLUMNS
# ============================================================

possible_a_columns = [
    "drug_a_ik14",
    "Drug_A",
    "drug_a",
    "drug1",
    "Drug1"
]

possible_b_columns = [
    "drug_b_ik14",
    "Drug_B",
    "drug_b",
    "drug2",
    "Drug2"
]

drug_a_column = None
drug_b_column = None

for col in possible_a_columns:
    if col in ddi_pairs.columns:
        drug_a_column = col
        break

for col in possible_b_columns:
    if col in ddi_pairs.columns:
        drug_b_column = col
        break

if drug_a_column is None or drug_b_column is None:
    raise ValueError(
        "Drug A / Drug B columns not found in DDI pair dataset"
    )

print(f"Drug A column: {drug_a_column}")
print(f"Drug B column: {drug_b_column}")


# ============================================================
# NORMALIZE IDS
# ============================================================

drug_features[drug_id_column] = (
    drug_features[drug_id_column]
    .astype(str)
    .str.strip()
)

ddi_pairs[drug_a_column] = (
    ddi_pairs[drug_a_column]
    .astype(str)
    .str.strip()
)

ddi_pairs[drug_b_column] = (
    ddi_pairs[drug_b_column]
    .astype(str)
    .str.strip()
)


# ============================================================
# CREATE LOOKUP TABLE
# ============================================================

feature_columns = [
    col for col in drug_features.columns
    if col != drug_id_column
]

print(f"Number of drug features: {len(feature_columns)}")


# ============================================================
# RENAME FEATURES FOR DRUG A
# ============================================================

drug_a_features = drug_features[
    [drug_id_column] + feature_columns
].copy()

drug_a_features = drug_a_features.rename(
    columns={
        drug_id_column: drug_a_column,
        **{
            col: f"A_{col}"
            for col in feature_columns
        }
    }
)


# ============================================================
# RENAME FEATURES FOR DRUG B
# ============================================================

drug_b_features = drug_features[
    [drug_id_column] + feature_columns
].copy()

drug_b_features = drug_b_features.rename(
    columns={
        drug_id_column: drug_b_column,
        **{
            col: f"B_{col}"
            for col in feature_columns
        }
    }
)


# ============================================================
# MERGE DRUG A FEATURES
# ============================================================

print("\nMerging Drug A features...")

pairs = ddi_pairs.merge(
    drug_a_features,
    on=drug_a_column,
    how="left"
)

print(f"After Drug A merge: {pairs.shape}")


# ============================================================
# MERGE DRUG B FEATURES
# ============================================================

print("Merging Drug B features...")

pairs = pairs.merge(
    drug_b_features,
    on=drug_b_column,
    how="left"
)

print(f"After Drug B merge: {pairs.shape}")


# ============================================================
# CHECK MISSING FEATURES
# ============================================================

a_feature_columns = [
    f"A_{col}" for col in feature_columns
]

b_feature_columns = [
    f"B_{col}" for col in feature_columns
]

missing_a = pairs[a_feature_columns].isna().all(axis=1).sum()
missing_b = pairs[b_feature_columns].isna().all(axis=1).sum()

print("\n" + "=" * 70)
print("MATCHING CHECK")
print("=" * 70)

print(f"Pairs without Drug A features: {missing_a}")
print(f"Pairs without Drug B features: {missing_b}")


# ============================================================
# REMOVE UNMATCHED PAIRS
# ============================================================

before = len(pairs)

pairs = pairs.dropna(
    subset=a_feature_columns + b_feature_columns,
    how="all"
)

after = len(pairs)

print(f"Rows before cleaning: {before}")
print(f"Rows after cleaning : {after}")


# ============================================================
# CREATE LABEL
# ============================================================

if "label" not in pairs.columns:
    if "Label" in pairs.columns:
        pairs = pairs.rename(columns={"Label": "label"})
    else:
        # RxPairEvid contains observed DDI pairs
        pairs["label"] = 1


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

identifier_columns = [
    drug_a_column,
    drug_b_column
]

existing_identifiers = [
    col for col in identifier_columns
    if col in pairs.columns
]

other_columns = [
    col for col in pairs.columns
    if col not in existing_identifiers
    and col not in a_feature_columns
    and col not in b_feature_columns
    and col != "label"
]

final_columns = (
    existing_identifiers
    + a_feature_columns
    + b_feature_columns
    + other_columns
    + ["label"]
)

pairs = pairs[
    [col for col in final_columns if col in pairs.columns]
]


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

pairs.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("PAIR FEATURE DATASET CREATED")
print("=" * 70)

print(f"Rows    : {pairs.shape[0]}")
print(f"Columns : {pairs.shape[1]}")
print(f"Drug A features : {len(a_feature_columns)}")
print(f"Drug B features : {len(b_feature_columns)}")
print(f"Label column    : label")

print(f"\nSaved: {OUTPUT_FILE}")

print("\nLabel distribution:")
print(pairs["label"].value_counts())

print("\nFirst 5 rows:")
print(pairs.head())