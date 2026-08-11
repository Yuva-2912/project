import os
import pandas as pd


# ============================================================
# FILES
# ============================================================

DDI_FILE = "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"
MASTER_FILE = "datasets/final/master_drug_table.csv"

OUTPUT_DIR = "datasets/processed"

SUMMARY_FILE = f"{OUTPUT_DIR}/ddi_dataset_summary.csv"
PAIR_FILE = f"{OUTPUT_DIR}/ddi_unique_pairs.csv"
DRUG_COVERAGE_FILE = f"{OUTPUT_DIR}/ddi_drug_coverage.csv"
DUPLICATE_FILE = f"{OUTPUT_DIR}/ddi_duplicate_pairs.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("DDI DATASET QUALITY & COVERAGE ANALYSIS")
print("=" * 70)

ddi = pd.read_csv(DDI_FILE)
master = pd.read_csv(MASTER_FILE)

print("\nDDI Dataset Shape :", ddi.shape)
print("Master Drug Count :", len(master))


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\nColumns:")
for col in ddi.columns:
    print("✓", col)


# ============================================================
# CLEAN NAMES
# ============================================================

ddi["a_name_clean"] = (
    ddi["a_name"]
    .astype(str)
    .str.strip()
    .str.lower()
)

ddi["b_name_clean"] = (
    ddi["b_name"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ============================================================
# SELF PAIRS
# ============================================================

self_pairs = ddi[
    ddi["a_name_clean"] == ddi["b_name_clean"]
].copy()


# ============================================================
# NORMALIZED PAIRS
# ============================================================

ddi["drug1"] = ddi[
    ["a_name_clean", "b_name_clean"]
].min(axis=1)

ddi["drug2"] = ddi[
    ["a_name_clean", "b_name_clean"]
].max(axis=1)

ddi["pair_key"] = (
    ddi["drug1"] + "||" + ddi["drug2"]
)


# ============================================================
# UNIQUE PAIRS
# ============================================================

unique_pairs = ddi[
    [
        "drug1",
        "drug2",
        "pair_key"
    ]
].drop_duplicates()


# ============================================================
# DUPLICATE PAIRS
# ============================================================

duplicate_pairs = ddi[
    ddi.duplicated(
        subset=["pair_key"],
        keep=False
    )
].copy()


# ============================================================
# UNIQUE DRUGS IN DDI
# ============================================================

ddi_drugs = set(
    ddi["a_name_clean"]
).union(
    set(ddi["b_name_clean"])
)


# ============================================================
# MASTER DRUGS
# ============================================================

master["DrugName_clean"] = (
    master["DrugName"]
    .astype(str)
    .str.strip()
    .str.lower()
)

master_drugs = set(
    master["DrugName_clean"]
)


# ============================================================
# NAME COVERAGE
# ============================================================

matched_drugs = (
    ddi_drugs.intersection(
        master_drugs
    )
)

unmatched_drugs = (
    ddi_drugs - master_drugs
)


# ============================================================
# DRUG FREQUENCY
# ============================================================

drug_a_counts = (
    ddi["a_name_clean"]
    .value_counts()
    .rename("DrugA_Count")
)

drug_b_counts = (
    ddi["b_name_clean"]
    .value_counts()
    .rename("DrugB_Count")
)

coverage = pd.DataFrame(
    index=sorted(ddi_drugs)
)

coverage.index.name = "DrugName"

coverage = coverage.join(
    drug_a_counts,
    how="left"
)

coverage = coverage.join(
    drug_b_counts,
    how="left"
)

coverage = coverage.fillna(0)

coverage["DrugA_Count"] = (
    coverage["DrugA_Count"]
    .astype(int)
)

coverage["DrugB_Count"] = (
    coverage["DrugB_Count"]
    .astype(int)
)

coverage["Total_DDI_Records"] = (
    coverage["DrugA_Count"]
    + coverage["DrugB_Count"]
)

coverage["In_Master_Dataset"] = (
    coverage.index.isin(
        master_drugs
    )
)

coverage = coverage.reset_index()


# ============================================================
# EVIDENCE STATISTICS
# ============================================================

evidence_columns = [
    "n_faers_reports",
    "faers_prr_max_strict",
    "faers_ror95_lcl_max_strict",
    "faers_pt_covered_strict",
    "faers_best_pt_code_strict"
]

evidence_summary = []

for column in evidence_columns:

    if column not in ddi.columns:
        continue

    evidence_summary.append({

        "Metric": column,

        "NonNull": ddi[column].notna().sum(),

        "Missing": ddi[column].isna().sum(),

        "UniqueValues": ddi[column].nunique()

    })


# ============================================================
# SUMMARY
# ============================================================

summary = [

    {
        "Metric": "Total DDI Records",
        "Value": len(ddi)
    },

    {
        "Metric": "Unique Drug Pairs",
        "Value": len(unique_pairs)
    },

    {
        "Metric": "Duplicate Pair Records",
        "Value": len(duplicate_pairs)
    },

    {
        "Metric": "Self Drug Pairs",
        "Value": len(self_pairs)
    },

    {
        "Metric": "Unique Drugs in DDI",
        "Value": len(ddi_drugs)
    },

    {
        "Metric": "DDI Drugs Matched to Master",
        "Value": len(matched_drugs)
    },

    {
        "Metric": "DDI Drugs Not Matched to Master",
        "Value": len(unmatched_drugs)
    },

    {
        "Metric": "Master Drugs",
        "Value": len(master_drugs)
    },

    {
        "Metric": "Master Drugs Appearing in DDI",
        "Value": len(
            matched_drugs
        )
    }

]

summary.extend(
    evidence_summary
)

summary_df = pd.DataFrame(
    summary
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

summary_df.to_csv(
    SUMMARY_FILE,
    index=False
)

unique_pairs.to_csv(
    PAIR_FILE,
    index=False
)

coverage.to_csv(
    DRUG_COVERAGE_FILE,
    index=False
)

duplicate_pairs.to_csv(
    DUPLICATE_FILE,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("DDI ANALYSIS COMPLETED ✅")
print("=" * 70)

print(
    "\nTotal DDI Records       :",
    len(ddi)
)

print(
    "Unique Drug Pairs       :",
    len(unique_pairs)
)

print(
    "Duplicate Pair Records  :",
    len(duplicate_pairs)
)

print(
    "Self Pairs              :",
    len(self_pairs)
)

print(
    "Unique DDI Drugs        :",
    len(ddi_drugs)
)

print(
    "Matched Master Drugs    :",
    len(matched_drugs)
)

print(
    "Unmatched Master Names  :",
    len(unmatched_drugs)
)

print("\nTop 20 Drugs by DDI Records:")

print(
    coverage
    .sort_values(
        "Total_DDI_Records",
        ascending=False
    )
    .head(20)
    .to_string(index=False)
)

print("\nOutput Files:")

print("✓", SUMMARY_FILE)
print("✓", PAIR_FILE)
print("✓", DRUG_COVERAGE_FILE)
print("✓", DUPLICATE_FILE)

print("\n" + "=" * 70)