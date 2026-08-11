import pandas as pd
import re
from pathlib import Path

print("=" * 70)
print("SIDER FUZZY MATCH REVIEW PREPARATION")
print("=" * 70)

# ---------------------------------------------------------
# FILES
# ---------------------------------------------------------
fuzzy_file = Path("datasets/processed/sider_fuzzy_review.csv")
master_file = Path("datasets/final/master_drug_table.csv")

output_file = Path("datasets/processed/sider_fuzzy_review_detailed.csv")

# ---------------------------------------------------------
# LOAD FUZZY CANDIDATES
# ---------------------------------------------------------
print("\nLoading fuzzy candidates...")

fuzzy = pd.read_csv(fuzzy_file)

print("Fuzzy candidates:", len(fuzzy))

# ---------------------------------------------------------
# LOAD MASTER
# ---------------------------------------------------------
print("\nLoading master drug table...")

master = pd.read_csv(master_file)

print("Master drugs:", len(master))

# Make CID numeric
master["CID"] = pd.to_numeric(master["CID"], errors="coerce")

# Candidate DrugID -> CID
drugid_to_cid = dict(
    zip(
        master["DrugID"],
        master["CID"]
    )
)

# ---------------------------------------------------------
# EXTRACT SIDER PUBCHEM CID
# ---------------------------------------------------------
def get_sider_cid(stitch_id):

    if pd.isna(stitch_id):
        return None

    match = re.fullmatch(
        r"CID(\d+)",
        str(stitch_id)
    )

    if not match:
        return None

    numeric_id = int(match.group(1))

    pubchem_cid = numeric_id - 100_000_000

    if pubchem_cid <= 0:
        return None

    return pubchem_cid


fuzzy["SIDER_PubChemCID"] = fuzzy["STITCH_ID"].apply(
    get_sider_cid
)

# ---------------------------------------------------------
# GET CANDIDATE CID
# ---------------------------------------------------------
fuzzy["CandidateCID"] = fuzzy["CandidateDrugID"].map(
    drugid_to_cid
)

# ---------------------------------------------------------
# CID COMPARISON
# ---------------------------------------------------------
fuzzy["CID_Match"] = (
    fuzzy["SIDER_PubChemCID"].notna()
    & fuzzy["CandidateCID"].notna()
    & (
        fuzzy["SIDER_PubChemCID"]
        == fuzzy["CandidateCID"]
    )
)

# ---------------------------------------------------------
# INITIAL REVIEW CATEGORY
# ---------------------------------------------------------
def classify(row):

    similarity = row["Similarity"]

    if row["CID_Match"]:
        return "ACCEPT_CID"

    if similarity >= 0.95:
        return "HIGH_SIMILARITY_REVIEW"

    if similarity >= 0.90:
        return "HIGH_REVIEW"

    if similarity >= 0.80:
        return "MEDIUM_REVIEW"

    return "LOW_REVIEW"


fuzzy["InitialReview"] = fuzzy.apply(
    classify,
    axis=1
)

# Empty column for manual verification
fuzzy["ReviewDecision"] = ""

# ---------------------------------------------------------
# REASON COLUMN
# ---------------------------------------------------------
def reason(row):

    if row["CID_Match"]:
        return "SIDER CID matches candidate CID"

    if row["Similarity"] >= 0.95:
        return "Very high name similarity but CID differs"

    if row["Similarity"] >= 0.90:
        return "High similarity; verify chemical identity"

    if row["Similarity"] >= 0.80:
        return "Moderate similarity; manual verification required"

    return "Low similarity; likely unsafe automatic match"


fuzzy["ReviewReason"] = fuzzy.apply(
    reason,
    axis=1
)

# ---------------------------------------------------------
# SORT
# ---------------------------------------------------------
fuzzy = fuzzy.sort_values(
    by=["CID_Match", "Similarity"],
    ascending=[False, False]
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
fuzzy.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 70)
print("REVIEW FILE CREATED")
print("=" * 70)

print("Rows:", len(fuzzy))
print("CID exact matches:", fuzzy["CID_Match"].sum())

print("\nInitial review categories:")
print(
    fuzzy["InitialReview"]
    .value_counts()
)

print("\nSimilarity >= 0.90:")
print(
    (fuzzy["Similarity"] >= 0.90).sum()
)

print("\nSimilarity >= 0.80:")
print(
    (fuzzy["Similarity"] >= 0.80).sum()
)

print("\nSaved:")
print(output_file)