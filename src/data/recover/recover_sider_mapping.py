
import pandas as pd
import re
import os


# ============================================================
# PATHS
# ============================================================

MASTER_PATH = "datasets/final/master_drug_table.csv"
SIDER_NAMES_PATH = "datasets/raw/SIDER/drug_names.tsv"
SIDER_SE_PATH = "datasets/raw/SIDER/meddra_all_se.tsv.gz"

OUTPUT_MAPPING = "datasets/processed/sider_drug_mapping.csv"
OUTPUT_SIDE_EFFECTS = "datasets/processed/drug_side_effects_recovered.csv"


# ============================================================
# NORMALIZE DRUG NAMES
# ============================================================

def normalize_name(name):

    if pd.isna(name):
        return ""

    name = str(name).lower().strip()

    # Greek letters
    name = name.replace("α", "alpha")
    name = name.replace("β", "beta")
    name = name.replace("γ", "gamma")

    # Common variations
    name = name.replace("-", " ")
    name = name.replace("_", " ")

    # Remove punctuation
    name = re.sub(r"[^a-z0-9]+", " ", name)

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name


# ============================================================
# LOAD MASTER
# ============================================================

print("=" * 70)
print("SIDER DRUGID RECOVERY - V2")
print("=" * 70)

master = pd.read_csv(MASTER_PATH)

print("\nMASTER")
print("Rows:", len(master))
print("Columns:", list(master.columns))

master["NormalizedName"] = master["DrugName"].apply(normalize_name)

master_names = master[
    ["DrugID", "DrugName", "NormalizedName"]
].copy()

master_names = master_names.drop_duplicates(
    subset=["NormalizedName"]
)

print("Unique master names:", len(master_names))


# ============================================================
# LOAD SIDER DRUG NAMES
# IMPORTANT: FILE HAS NO HEADER
# ============================================================

print("\nLoading SIDER drug_names.tsv...")

sider_names = pd.read_csv(
    SIDER_NAMES_PATH,
    sep="\t",
    header=None,
    dtype=str
)

# Explicitly assign columns
sider_names.columns = [
    "STITCH_ID",
    "DrugName"
]

print("SIDER drug_names shape:", sider_names.shape)

print("\nSIDER columns:")
print(list(sider_names.columns))

print("\nFirst 5 SIDER rows:")
print(sider_names.head().to_string(index=False))


# ============================================================
# NORMALIZE SIDER NAMES
# ============================================================

sider_names["NormalizedName"] = (
    sider_names["DrugName"]
    .apply(normalize_name)
)


# ============================================================
# EXACT NORMALIZED NAME MATCH
# ============================================================

print("\nMatching SIDER drugs with master...")

mapping = sider_names.merge(
    master_names,
    on="NormalizedName",
    how="left",
    suffixes=("_SIDER", "_MASTER")
)


# ============================================================
# MATCH STATUS
# ============================================================

mapping["MatchStatus"] = mapping["DrugID"].notna().map({
    True: "Matched",
    False: "Unmatched"
})


matched = mapping[
    mapping["DrugID"].notna()
].copy()

unmatched = mapping[
    mapping["DrugID"].isna()
].copy()


print("\n" + "=" * 70)
print("SIDER NAME MATCH RESULTS")
print("=" * 70)

print("SIDER drugs:", len(mapping))
print("Matched:", len(matched))
print("Unmatched:", len(unmatched))


# ============================================================
# SAVE MAPPING
# ============================================================

mapping[
    [
        "STITCH_ID",
        "DrugName_SIDER",
        "DrugID",
        "DrugName_MASTER",
        "MatchStatus"
    ]
].to_csv(
    OUTPUT_MAPPING,
    index=False
)

print("\nSaved mapping:")
print(OUTPUT_MAPPING)


# ============================================================
# SHOW UNMATCHED DRUGS
# ============================================================

if len(unmatched) > 0:

    print("\n" + "=" * 70)
    print("UNMATCHED SIDER DRUGS")
    print("=" * 70)

    print(
        unmatched[
            ["STITCH_ID", "DrugName_SIDER"]
        ].to_string(index=False)
    )


# ============================================================
# LOAD SIDER SIDE EFFECT DATA
# ============================================================

print("\n" + "=" * 70)
print("LOADING SIDER SIDE EFFECT DATA")
print("=" * 70)

sider_se = pd.read_csv(
    SIDER_SE_PATH,
    sep="\t",
    header=None,
    dtype=str
)

print("Raw SIDER side-effect shape:", sider_se.shape)


# ============================================================
# SIDER MEDDRA COLUMNS
# ============================================================

# SIDER meddra_all_se.tsv structure:
#
# STITCH compound ID
# STITCH compound ID flat
# UMLS concept ID
# MedDRA type
# MedDRA concept ID
# MedDRA concept name

if sider_se.shape[1] >= 6:

    sider_se = sider_se.iloc[:, :6]

    sider_se.columns = [
        "STITCH_ID",
        "STITCH_ID_FLAT",
        "UMLS_ID",
        "MedDRA_Type",
        "MedDRA_ID",
        "SideEffect"
    ]

else:

    raise ValueError(
        "Unexpected SIDER side-effect file format. "
        f"Expected at least 6 columns, got {sider_se.shape[1]}"
    )


# ============================================================
# BUILD STITCH -> DRUGID MAP
# ============================================================

stitch_map = mapping[
    [
        "STITCH_ID",
        "DrugID",
        "DrugName_MASTER"
    ]
].copy()

stitch_map = stitch_map.dropna(
    subset=["DrugID"]
)

stitch_map = stitch_map.drop_duplicates(
    subset=["STITCH_ID"]
)

print("\nMatched STITCH IDs:", len(stitch_map))


# ============================================================
# NORMALIZE STITCH IDs
# ============================================================

sider_se["STITCH_ID"] = (
    sider_se["STITCH_ID"]
    .astype(str)
    .str.strip()
)

stitch_map["STITCH_ID"] = (
    stitch_map["STITCH_ID"]
    .astype(str)
    .str.strip()
)


# ============================================================
# MERGE SIDE EFFECTS WITH DRUG IDs
# ============================================================

print("\nMapping SIDER side effects to DrugID...")

recovered = sider_se.merge(
    stitch_map,
    on="STITCH_ID",
    how="inner"
)


# ============================================================
# FINAL SIDE EFFECT TABLE
# ============================================================

recovered = recovered[
    [
        "DrugID",
        "DrugName_MASTER",
        "SideEffect"
    ]
].copy()

recovered.columns = [
    "DrugID",
    "DrugName",
    "SideEffect"
]

recovered = recovered.dropna(
    subset=["DrugID", "SideEffect"]
)

recovered = recovered.drop_duplicates()

recovered["DrugID"] = (
    recovered["DrugID"]
    .astype(int)
)


# ============================================================
# SAVE RECOVERED SIDE EFFECTS
# ============================================================

recovered.to_csv(
    OUTPUT_SIDE_EFFECTS,
    index=False
)


# ============================================================
# COVERAGE
# ============================================================

unique_sider_drugs = (
    recovered["DrugID"]
    .nunique()
)

missing = len(master) - unique_sider_drugs

coverage = (
    unique_sider_drugs /
    len(master)
    * 100
)


print("\n" + "=" * 70)
print("SIDER RECOVERY SUMMARY")
print("=" * 70)

print("Master drugs          :", len(master))
print("SIDER source drugs    :", len(sider_names))
print("Matched SIDER drugs   :", len(matched))
print("Unmatched SIDER drugs :", len(unmatched))
print("Mapped DrugIDs        :", unique_sider_drugs)
print("Missing from SIDER    :", missing)
print("SIDER coverage        :", f"{coverage:.2f}%")
print("Side-effect records   :", len(recovered))

print("\nSaved:")
print(OUTPUT_MAPPING)
print(OUTPUT_SIDE_EFFECTS)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

