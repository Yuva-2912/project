import os
import pandas as pd


# ============================================================
# FILES
# ============================================================

DDI_FILE = "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"
MASTER_FILE = "datasets/final/master_drug_table.csv"

OUTPUT_FILE = "datasets/final/ddi_evidence_table.csv"


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("CREATING DDI EVIDENCE MASTER TABLE")
print("=" * 70)

ddi = pd.read_csv(DDI_FILE)
master = pd.read_csv(MASTER_FILE)

print("\nDDI Records   :", len(ddi))
print("Master Drugs  :", len(master))


# ============================================================
# CLEAN DRUG NAMES
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

master["DrugName_clean"] = (
    master["DrugName"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ============================================================
# CREATE DRUG ID MAP
# ============================================================

drug_id_map = dict(
    zip(
        master["DrugName_clean"],
        master["DrugID"]
    )
)


# ============================================================
# MAP DRUG IDs
# ============================================================

ddi["DrugA_ID"] = ddi[
    "a_name_clean"
].map(drug_id_map)

ddi["DrugB_ID"] = ddi[
    "b_name_clean"
].map(drug_id_map)


# ============================================================
# CREATE EVIDENCE TABLE
# ============================================================

evidence = pd.DataFrame({

    "DrugA_ID":
        ddi["DrugA_ID"],

    "DrugB_ID":
        ddi["DrugB_ID"],

    "DrugA_Name":
        ddi["a_name"],

    "DrugB_Name":
        ddi["b_name"],

    "DrugA_Ik14":
        ddi["drug_a_ik14"],

    "DrugB_Ik14":
        ddi["drug_b_ik14"],

    "Pair_ID":
        ddi["pair_id"],

    # --------------------------------------------------------
    # DDI EVIDENCE
    # --------------------------------------------------------

    "FAERS_Report_Count":
        ddi["n_faers_reports"],

    "FAERS_PRR_Max_Strict":
        ddi["faers_prr_max_strict"],

    "FAERS_ROR95_LCL_Max_Strict":
        ddi["faers_ror95_lcl_max_strict"],

    "FAERS_PT_Covered_Strict":
        ddi["faers_pt_covered_strict"],

    "FAERS_Best_PT_Code":
        ddi["faers_best_pt_code_strict"]

})


# ============================================================
# INTERACTION LABEL
# ============================================================

# Every record in RxPairEvid represents an observed/evidenced
# DDI pair.

evidence["Interaction"] = 1


# ============================================================
# EVIDENCE AVAILABILITY
# ============================================================

evidence["Has_FAERS_Evidence"] = (
    evidence["FAERS_Report_Count"]
    .notna()
    &
    (
        pd.to_numeric(
            evidence["FAERS_Report_Count"],
            errors="coerce"
        )
        > 0
    )
)


evidence["Has_PRR_Evidence"] = (
    evidence["FAERS_PRR_Max_Strict"]
    .notna()
)


evidence["Has_ROR_Evidence"] = (
    evidence["FAERS_ROR95_LCL_Max_Strict"]
    .notna()
)


evidence["Has_PT_Evidence"] = (
    evidence["FAERS_Best_PT_Code"]
    .notna()
)


# ============================================================
# EVIDENCE STRENGTH CATEGORY
# ============================================================

evidence["EvidenceLevel"] = "No quantitative evidence"

evidence.loc[
    evidence["Has_FAERS_Evidence"],
    "EvidenceLevel"
] = "FAERS evidence"

evidence.loc[
    evidence["Has_FAERS_Evidence"]
    &
    evidence["Has_PRR_Evidence"],
    "EvidenceLevel"
] = "FAERS + PRR evidence"

evidence.loc[
    evidence["Has_FAERS_Evidence"]
    &
    evidence["Has_PRR_Evidence"]
    &
    evidence["Has_ROR_Evidence"],
    "EvidenceLevel"
] = "FAERS + PRR + ROR evidence"


# ============================================================
# REMOVE TEMP COLUMNS
# ============================================================

evidence = evidence.drop(
    columns=[]
)


# ============================================================
# VALIDATION
# ============================================================

print("\nValidation")
print("-" * 70)

print(
    "Total pairs           :",
    len(evidence)
)

print(
    "Missing DrugA IDs     :",
    evidence["DrugA_ID"].isna().sum()
)

print(
    "Missing DrugB IDs     :",
    evidence["DrugB_ID"].isna().sum()
)

print(
    "Duplicate Pair IDs    :",
    evidence["Pair_ID"].duplicated().sum()
)

print(
    "FAERS Evidence        :",
    evidence["Has_FAERS_Evidence"].sum()
)

print(
    "PRR Evidence          :",
    evidence["Has_PRR_Evidence"].sum()
)

print(
    "ROR Evidence          :",
    evidence["Has_ROR_Evidence"].sum()
)

print(
    "PT Evidence           :",
    evidence["Has_PT_Evidence"].sum()
)


# ============================================================
# CHECK ALL DRUGS
# ============================================================

used_drugs = set(
    evidence["DrugA_ID"].dropna().astype(int)
).union(
    set(
        evidence["DrugB_ID"]
        .dropna()
        .astype(int)
    )
)

master_drug_ids = set(
    master["DrugID"].astype(int)
)

missing_drugs = (
    master_drug_ids - used_drugs
)

print(
    "Master drugs not in DDI:",
    len(missing_drugs)
)


# ============================================================
# EVIDENCE DISTRIBUTION
# ============================================================

print("\nEvidence Distribution")
print("-" * 70)

print(
    evidence["EvidenceLevel"]
    .value_counts()
    .to_string()
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

evidence.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# PREVIEW
# ============================================================

print("\nPreview:")
print(
    evidence.head(10)
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("DDI EVIDENCE MASTER TABLE CREATED ✅")
print("=" * 70)

print(
    "\nOutput:",
    OUTPUT_FILE
)