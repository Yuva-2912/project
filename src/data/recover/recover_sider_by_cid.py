import pandas as pd
import os
import re

print("=" * 70)
print("SIDER → PUBCHEM CID → DRUGID RECOVERY")
print("=" * 70)

# ============================================================
# PATHS
# ============================================================

MASTER_PATH = "datasets/final/master_drug_table.csv"
SIDER_NAMES_PATH = "datasets/raw/SIDER/drug_names.tsv"
SIDER_SE_PATH = "datasets/raw/SIDER/meddra_all_se.tsv.gz"

MAPPING_OUTPUT = "datasets/processed/sider_drug_mapping.csv"
SIDER_OUTPUT = "datasets/processed/drug_side_effects_recovered.csv"

# ============================================================
# LOAD MASTER
# ============================================================

print("\nLoading master dataset...")

master = pd.read_csv(MASTER_PATH)

print("Master shape:", master.shape)
print("Master drugs:", master["DrugID"].nunique())

# Make sure CID is numeric
master["CID"] = pd.to_numeric(master["CID"], errors="coerce")

master_cid = master.dropna(subset=["CID"]).copy()

master_cid["CID"] = master_cid["CID"].astype("int64")

cid_to_drugid = dict(
    zip(master_cid["CID"], master_cid["DrugID"])
)

cid_to_name = dict(
    zip(master_cid["CID"], master_cid["DrugName"])
)

print("Master drugs with CID:", len(cid_to_drugid))

# ============================================================
# LOAD SIDER DRUG NAMES
# ============================================================

print("\nLoading SIDER drug_names.tsv...")

sider_names = pd.read_csv(
    SIDER_NAMES_PATH,
    sep="\t",
    header=None,
    names=["STITCH_ID", "SIDER_DrugName"],
    dtype=str
)

print("SIDER source drugs:", len(sider_names))

# ============================================================
# CONVERT STITCH CID → PUBCHEM CID
# ============================================================

def stitch_to_pubchem(stitch_id):

    if pd.isna(stitch_id):
        return None

    stitch_id = str(stitch_id).strip()

    # Expected format:
    # CID100002244

    match = re.fullmatch(r"CID(\d+)", stitch_id)

    if not match:
        return None

    numeric_id = int(match.group(1))

    # SIDER/STITCH CID convention
    # PubChem CID + 100,000,000
    pubchem_cid = numeric_id - 100_000_000

    if pubchem_cid <= 0:
        return None

    return pubchem_cid


sider_names["PubChemCID"] = sider_names["STITCH_ID"].apply(
    stitch_to_pubchem
)

print(
    "SIDER rows with converted PubChem CID:",
    sider_names["PubChemCID"].notna().sum()
)

# ============================================================
# MAP TO MASTER DRUGID
# ============================================================

sider_names["DrugID"] = sider_names["PubChemCID"].map(
    cid_to_drugid
)

sider_names["MasterDrugName"] = sider_names["PubChemCID"].map(
    cid_to_name
)

matched = sider_names[sider_names["DrugID"].notna()].copy()
unmatched = sider_names[sider_names["DrugID"].isna()].copy()

print("\n" + "=" * 70)
print("CID MAPPING SUMMARY")
print("=" * 70)

print("SIDER source drugs :", len(sider_names))
print("CID converted      :", sider_names["PubChemCID"].notna().sum())
print("Matched Master     :", len(matched))
print("Unmatched          :", len(unmatched))
print("Unique DrugIDs     :", matched["DrugID"].nunique())

coverage = (
    matched["DrugID"].nunique()
    / master["DrugID"].nunique()
    * 100
)

print(f"SIDER drug coverage : {coverage:.2f}%")

# ============================================================
# SHOW MATCHES
# ============================================================

print("\nFirst 20 verified mappings:")

print(
    matched[
        [
            "STITCH_ID",
            "SIDER_DrugName",
            "PubChemCID",
            "DrugID",
            "MasterDrugName"
        ]
    ].head(20).to_string(index=False)
)

# ============================================================
# SAVE MAPPING
# ============================================================

mapping = matched[
    [
        "STITCH_ID",
        "SIDER_DrugName",
        "PubChemCID",
        "DrugID",
        "MasterDrugName"
    ]
].copy()

mapping.to_csv(
    MAPPING_OUTPUT,
    index=False
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
    compression="gzip",
    dtype=str
)

print("Raw SIDER side-effect shape:", sider_se.shape)

print("\nSIDER columns:")
print(list(sider_se.columns))

# SIDER meddra_all_se.tsv.gz format:
#
# 0 = STITCH compound ID
# 1 = STITCH flat compound ID
# 2 = MedDRA type
# 3 = MedDRA concept ID
# 4 = MedDRA concept name
# 5 = UMLS concept ID

sider_se = sider_se.rename(
    columns={
        0: "STITCH_ID",
        1: "STITCH_Flat_ID",
        2: "MedDRA_Type",
        3: "MedDRA_ID",
        4: "SideEffect",
        5: "UMLS_ID"
    }
)

# ============================================================
# MERGE SIDE EFFECTS WITH DRUG MAPPING
# ============================================================

print("\nMapping SIDER side effects to DrugID...")

side_effects = sider_se.merge(
    mapping[
        [
            "STITCH_ID",
            "DrugID",
            "MasterDrugName"
        ]
    ],
    on="STITCH_ID",
    how="inner"
)

print(
    "Matched side-effect records:",
    len(side_effects)
)

# ============================================================
# CLEAN FINAL SIDER DATA
# ============================================================

side_effects_final = side_effects[
    [
        "DrugID",
        "MasterDrugName",
        "SideEffect"
    ]
].copy()

side_effects_final = side_effects_final.rename(
    columns={
        "MasterDrugName": "DrugName"
    }
)

# Remove empty side effects
side_effects_final["SideEffect"] = (
    side_effects_final["SideEffect"]
    .astype(str)
    .str.strip()
)

side_effects_final = side_effects_final[
    side_effects_final["SideEffect"].notna()
]

# Remove duplicates
side_effects_final = side_effects_final.drop_duplicates()

# ============================================================
# SAVE
# ============================================================

side_effects_final.to_csv(
    SIDER_OUTPUT,
    index=False
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL SIDER RECOVERY")
print("=" * 70)

print("Master drugs             :", master["DrugID"].nunique())
print("SIDER source drugs       :", len(sider_names))
print("SIDER → Master matched   :", matched["DrugID"].nunique())

print(
    "Drugs with side effects  :",
    side_effects_final["DrugID"].nunique()
)

print(
    "Side-effect records      :",
    len(side_effects_final)
)

final_coverage = (
    side_effects_final["DrugID"].nunique()
    / master["DrugID"].nunique()
    * 100
)

print(f"Final SIDER coverage     : {final_coverage:.2f}%")

print("\nSaved:")
print(MAPPING_OUTPUT)
print(SIDER_OUTPUT)

print("\n" + "=" * 70)
print("SIDER RECOVERY COMPLETED")
print("=" * 70)