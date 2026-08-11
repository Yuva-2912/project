import pandas as pd
import re
from difflib import SequenceMatcher

MASTER_PATH = "datasets/final/master_drug_table.csv"
SIDER_MAPPING_PATH = "datasets/processed/sider_drug_mapping.csv"
SIDER_NAMES_PATH = "datasets/raw/SIDER/drug_names.tsv"

OUTPUT = "datasets/processed/sider_unmatched_candidates.csv"


def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()

    # common chemical punctuation
    name = name.replace("-", " ")
    name = name.replace("_", " ")
    name = name.replace("/", " ")
    name = name.replace(",", " ")
    name = name.replace("(", " ")
    name = name.replace(")", " ")
    name = name.replace("[", " ")
    name = name.replace("]", " ")

    # remove extra spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name


print("=" * 70)
print("ANALYZING UNMATCHED SIDER DRUGS")
print("=" * 70)

# ============================================================
# LOAD MASTER
# ============================================================

master = pd.read_csv(MASTER_PATH)

master["NormalizedName"] = master["DrugName"].apply(
    normalize_name
)

print("Master drugs:", len(master))

# ============================================================
# LOAD SIDER
# ============================================================

sider = pd.read_csv(
    SIDER_NAMES_PATH,
    sep="\t",
    header=None,
    names=["STITCH_ID", "SIDER_DrugName"],
    dtype=str
)

sider["NormalizedName"] = sider["SIDER_DrugName"].apply(
    normalize_name
)

# ============================================================
# LOAD EXISTING CID MAPPING
# ============================================================

mapping = pd.read_csv(
    SIDER_MAPPING_PATH
)

matched_stitch = set(
    mapping["STITCH_ID"].astype(str)
)

unmatched = sider[
    ~sider["STITCH_ID"].isin(matched_stitch)
].copy()

print("SIDER drugs:", len(sider))
print("Already matched:", len(matched_stitch))
print("Unmatched:", len(unmatched))

# ============================================================
# EXACT NORMALIZED NAME MATCH
# ============================================================

master_name_map = {}

for _, row in master.iterrows():

    name = row["NormalizedName"]

    if not name:
        continue

    if name not in master_name_map:
        master_name_map[name] = []

    master_name_map[name].append(
        (
            row["DrugID"],
            row["DrugName"]
        )
    )

results = []

for _, sider_row in unmatched.iterrows():

    sider_name = sider_row["SIDER_DrugName"]
    normalized = sider_row["NormalizedName"]

    candidates = master_name_map.get(
        normalized,
        []
    )

    if len(candidates) == 1:

        drug_id, drug_name = candidates[0]

        results.append({
            "STITCH_ID": sider_row["STITCH_ID"],
            "SIDER_DrugName": sider_name,
            "MatchType": "EXACT_NORMALIZED",
            "Confidence": "HIGH",
            "CandidateDrugID": drug_id,
            "CandidateDrugName": drug_name,
            "Similarity": 1.0
        })

# ============================================================
# FUZZY CANDIDATES
# ============================================================

print("\nGenerating fuzzy candidates...")

master_names = list(
    master_name_map.keys()
)

already_exact = set(
    r["STITCH_ID"]
    for r in results
)

for _, sider_row in unmatched.iterrows():

    stitch_id = sider_row["STITCH_ID"]

    if stitch_id in already_exact:
        continue

    sider_name = sider_row["SIDER_DrugName"]
    normalized = sider_row["NormalizedName"]

    if not normalized:
        continue

    best_matches = []

    for master_name in master_names:

        similarity = SequenceMatcher(
            None,
            normalized,
            master_name
        ).ratio()

        if similarity >= 0.70:

            for drug_id, drug_name in master_name_map[
                master_name
            ]:

                best_matches.append(
                    (
                        similarity,
                        drug_id,
                        drug_name
                    )
                )

    best_matches.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    for similarity, drug_id, drug_name in best_matches[:3]:

        results.append({
            "STITCH_ID": stitch_id,
            "SIDER_DrugName": sider_name,
            "MatchType": "FUZZY_CANDIDATE",
            "Confidence": "REVIEW",
            "CandidateDrugID": drug_id,
            "CandidateDrugName": drug_name,
            "Similarity": round(similarity, 4)
        })

# ============================================================
# SAVE
# ============================================================

result_df = pd.DataFrame(results)

result_df = result_df.sort_values(
    [
        "MatchType",
        "Similarity"
    ],
    ascending=[True, False]
)

result_df.to_csv(
    OUTPUT,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("UNMATCHED SIDER ANALYSIS")
print("=" * 70)

print(
    "Original unmatched SIDER drugs:",
    len(unmatched)
)

print(
    "Exact normalized matches:",
    (result_df["MatchType"] == "EXACT_NORMALIZED").sum()
)

print(
    "Fuzzy candidates:",
    (result_df["MatchType"] == "FUZZY_CANDIDATE").sum()
)

print("\nSaved:")
print(OUTPUT)

print("=" * 70)
print("DONE")
print("=" * 70)