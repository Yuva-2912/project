import pandas as pd
import re
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(r"D:\DDL")

UNIFIED_FILE = BASE_DIR / "datasets/final/unified_drug_features.csv"
DDI_FILE = BASE_DIR / "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"

OUTPUT_MAPPING = BASE_DIR / "datasets/final/ddi_drug_id_mapping.csv"
OUTPUT_DDI = BASE_DIR / "datasets/final/ddi_pairs_with_drug_ids.csv"


# ============================================================
# NORMALIZE DRUG NAMES
# ============================================================

def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    # Normalize whitespace
    name = re.sub(r"\s+", " ", name)

    # Remove surrounding spaces
    name = name.strip()

    return name


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("LOADING DATA")
print("=" * 70)

unified = pd.read_csv(UNIFIED_FILE, low_memory=False)
ddi = pd.read_csv(DDI_FILE, low_memory=False)

print(f"Unified drug features : {unified.shape}")
print(f"DDI pairs             : {ddi.shape}")


# ============================================================
# CREATE NORMALIZED NAME COLUMNS
# ============================================================

unified["name_normalized"] = unified["DrugName"].apply(normalize_name)

ddi["a_name_normalized"] = ddi["a_name"].apply(normalize_name)
ddi["b_name_normalized"] = ddi["b_name"].apply(normalize_name)


# ============================================================
# CHECK DUPLICATE UNIFIED DRUG NAMES
# ============================================================

duplicate_names = (
    unified[unified["name_normalized"].duplicated(keep=False)]
    .sort_values("name_normalized")
)

print("\n" + "=" * 70)
print("DUPLICATE NAME CHECK")
print("=" * 70)

print(f"Duplicate unified drug-name rows: {len(duplicate_names)}")
print(
    f"Unique duplicated names: "
    f"{duplicate_names['name_normalized'].nunique()}"
)


# ============================================================
# CREATE NAME -> DRUGID MAP
# ============================================================

# Only use unique drug names directly.
# If the same normalized name occurs multiple times,
# we keep the first DrugID and report duplicates separately.

name_to_drug_id = (
    unified
    .drop_duplicates("name_normalized", keep="first")
    .set_index("name_normalized")["DrugID"]
    .to_dict()
)


# ============================================================
# MAP DRUG A
# ============================================================

ddi["DrugA_ID"] = ddi["a_name_normalized"].map(name_to_drug_id)

# ============================================================
# MAP DRUG B
# ============================================================

ddi["DrugB_ID"] = ddi["b_name_normalized"].map(name_to_drug_id)


# ============================================================
# MATCHING CHECK
# ============================================================

a_matched = ddi["DrugA_ID"].notna()
b_matched = ddi["DrugB_ID"].notna()

print("\n" + "=" * 70)
print("DRUG ID MATCHING CHECK")
print("=" * 70)

print(f"Drug A matched     : {a_matched.sum()}")
print(f"Drug A unmatched   : {(~a_matched).sum()}")

print(f"Drug B matched     : {b_matched.sum()}")
print(f"Drug B unmatched   : {(~b_matched).sum()}")

print(
    f"Both matched       : "
    f"{(a_matched & b_matched).sum()}"
)

print(
    f"Either unmatched   : "
    f"{(~(a_matched & b_matched)).sum()}"
)


# ============================================================
# SHOW UNMATCHED DRUGS
# ============================================================

unmatched_a = (
    ddi.loc[~a_matched, ["drug_a_ik14", "a_name"]]
    .drop_duplicates()
)

unmatched_b = (
    ddi.loc[~b_matched, ["drug_b_ik14", "b_name"]]
    .drop_duplicates()
)

print("\n" + "=" * 70)
print("UNMATCHED DRUG A")
print("=" * 70)

print(unmatched_a.head(30).to_string(index=False))

print("\n" + "=" * 70)
print("UNMATCHED DRUG B")
print("=" * 70)

print(unmatched_b.head(30).to_string(index=False))


# ============================================================
# CREATE INCHTIKEY -> DRUGID MAPPING
# ============================================================

mapping_a = ddi[
    ["drug_a_ik14", "a_name", "DrugA_ID"]
].copy()

mapping_a.columns = [
    "InChIKey14",
    "DrugName",
    "DrugID"
]

mapping_a["Source"] = "Drug_A"


mapping_b = ddi[
    ["drug_b_ik14", "b_name", "DrugB_ID"]
].copy()

mapping_b.columns = [
    "InChIKey14",
    "DrugName",
    "DrugID"
]

mapping_b["Source"] = "Drug_B"


mapping = pd.concat(
    [mapping_a, mapping_b],
    ignore_index=True
)

mapping = mapping.dropna(subset=["DrugID"])

mapping["DrugID"] = mapping["DrugID"].astype(int)

mapping["DrugName_Normalized"] = mapping["DrugName"].apply(
    normalize_name
)

mapping = mapping.drop_duplicates(
    subset=["InChIKey14"],
    keep="first"
)

mapping = mapping.sort_values("DrugID")


# ============================================================
# SAVE MAPPING
# ============================================================

OUTPUT_MAPPING.parent.mkdir(
    parents=True,
    exist_ok=True
)

mapping.to_csv(
    OUTPUT_MAPPING,
    index=False
)


# ============================================================
# CLEAN DDI DATASET
# ============================================================

ddi["DrugA_ID"] = ddi["DrugA_ID"].astype("Int64")
ddi["DrugB_ID"] = ddi["DrugB_ID"].astype("Int64")

# Remove temporary normalized columns
ddi_clean = ddi.drop(
    columns=[
        "a_name_normalized",
        "b_name_normalized"
    ]
)


# ============================================================
# SAVE UPDATED DDI DATASET
# ============================================================

ddi_clean.to_csv(
    OUTPUT_DDI,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("MAPPING CREATED SUCCESSFULLY")
print("=" * 70)

print(f"Unique mapped InChIKey14 : {mapping['InChIKey14'].nunique()}")
print(f"Unique mapped DrugID     : {mapping['DrugID'].nunique()}")

print(f"\nSaved mapping:")
print(OUTPUT_MAPPING)

print(f"\nSaved DDI dataset:")
print(OUTPUT_DDI)

print("\nFirst 10 mappings:")
print(
    mapping[
        ["InChIKey14", "DrugName", "DrugID"]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("COMPLETED")
print("=" * 70)