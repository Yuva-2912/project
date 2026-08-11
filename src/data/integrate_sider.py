import os
import re
import pandas as pd

# ============================================================
# FILES
# ============================================================

MASTER_FILE = "datasets/final/master_drug_table.csv"

SIDER_NAMES_FILE = "datasets/raw/SIDER/drug_names.tsv"

SIDER_SE_FILE = "datasets/raw/SIDER/meddra_all_se.tsv.gz"

OUTPUT_FILE = "datasets/processed/drug_side_effects.csv"

UNMATCHED_FILE = "datasets/processed/sider_unmatched_drugs.csv"


# ============================================================
# FUNCTION
# ============================================================

def convert_sider_cid(value):

    """
    Convert SIDER CID format:

        CID100000085 -> 85

    """

    value = str(value).strip()

    match = re.search(r"CID(\d+)", value)

    if match:

        number = int(match.group(1))

        # SIDER uses 100000000 offset
        if number >= 100000000:
            return number - 100000000

        return number

    return None


# ============================================================
# LOAD MASTER
# ============================================================

master = pd.read_csv(
    MASTER_FILE
)

print("=" * 70)
print("SIDER Integration")
print("=" * 70)

print(
    "\nMaster Drug Table :",
    master.shape
)


# ============================================================
# LOAD SIDER DRUG NAMES
# ============================================================

sider_names = pd.read_csv(
    SIDER_NAMES_FILE,
    sep="\t",
    header=None,
    dtype=str
)

sider_names = sider_names.iloc[:, :2]

sider_names.columns = [
    "SIDER_CID",
    "SIDER_DrugName"
]

print(
    "SIDER Drug Names :",
    sider_names.shape
)


# ============================================================
# LOAD SIDER SIDE EFFECTS
# ============================================================

sider_se = pd.read_csv(
    SIDER_SE_FILE,
    sep="\t",
    header=None,
    dtype=str,
    compression="gzip"
)

print(
    "SIDER Side Effects :",
    sider_se.shape
)


# ============================================================
# EXTRACT CID + SIDE EFFECT
# ============================================================

sider_se = sider_se.iloc[:, [0, 5]]

sider_se.columns = [
    "SIDER_CID",
    "SideEffect"
]


# ============================================================
# CONVERT SIDER CID
# ============================================================

sider_names["CID_key"] = (
    sider_names["SIDER_CID"]
    .apply(convert_sider_cid)
)

sider_se["CID_key"] = (
    sider_se["SIDER_CID"]
    .apply(convert_sider_cid)
)


# ============================================================
# MASTER CID
# ============================================================

master["CID_key"] = pd.to_numeric(
    master["CID"],
    errors="coerce"
)


# ============================================================
# REMOVE INVALID SIDE EFFECTS
# ============================================================

sider_se = sider_se[
    sider_se["CID_key"].notna()
].copy()

sider_se["SideEffect"] = (
    sider_se["SideEffect"]
    .astype(str)
    .str.strip()
)

sider_se = sider_se[
    (sider_se["SideEffect"] != "") &
    (sider_se["SideEffect"].str.lower() != "nan")
]


# ============================================================
# MERGE
# ============================================================

merged = sider_se.merge(
    master[
        [
            "DrugID",
            "DrugName",
            "CID_key"
        ]
    ],
    on="CID_key",
    how="inner"
)


# ============================================================
# FINAL DATASET
# ============================================================

final = merged[
    [
        "DrugID",
        "DrugName",
        "SideEffect"
    ]
].copy()


# ============================================================
# REMOVE DUPLICATES
# ============================================================

final = final.drop_duplicates(
    subset=[
        "DrugID",
        "SideEffect"
    ]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

final.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# UNMATCHED SIDER DRUGS
# ============================================================

master_cids = set(
    master["CID_key"]
    .dropna()
)

sider_cids = set(
    sider_names["CID_key"]
    .dropna()
)

unmatched_cids = sider_cids - master_cids

unmatched = sider_names[
    sider_names["CID_key"].isin(
        unmatched_cids
    )
][
    [
        "SIDER_CID",
        "SIDER_DrugName"
    ]
].drop_duplicates()


unmatched.to_csv(
    UNMATCHED_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SIDER Integration Completed ✅")
print("=" * 70)

print(
    "Master Drugs              :",
    master["DrugID"].nunique()
)

print(
    "SIDER Drug Names          :",
    sider_names["CID_key"].nunique()
)

print(
    "Raw Side Effect Records   :",
    len(sider_se)
)

print(
    "Matched Drugs             :",
    final["DrugID"].nunique()
)

print(
    "Final Side Effect Records :",
    len(final)
)

print(
    "Unmatched SIDER Drugs     :",
    len(unmatched)
)

print("\nFinal Dataset Preview:")
print(
    final.head(10).to_string(
        index=False
    )
)

print("\nFiles Created:")
print("✓", OUTPUT_FILE)
print("✓", UNMATCHED_FILE)