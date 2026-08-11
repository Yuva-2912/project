import os
import pandas as pd

# ---------------------------------------
# Files
# ---------------------------------------

MASTER_FILE = "datasets/processed/master_drug_list.csv"
PUBCHEM_FILE = "datasets/processed/pubchem_data_result.csv"

OUTPUT_DIR = "datasets/processed"

VALIDATION_FILE = os.path.join(
    OUTPUT_DIR,
    "pubchem_validation_report.csv"
)

MISSING_FILE = os.path.join(
    OUTPUT_DIR,
    "missing_pubchem_drugs.csv"
)

# ---------------------------------------
# Load Files
# ---------------------------------------

master = pd.read_csv(MASTER_FILE)
pubchem = pd.read_csv(PUBCHEM_FILE)

# ---------------------------------------
# Required Columns
# ---------------------------------------

required_columns = [
    "DrugName",
    "CID",
    "ConnectivitySMILES",
    "MolecularWeight",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount"
]

# ---------------------------------------
# Normalize Names
# ---------------------------------------

master["DrugName_key"] = (
    master["DrugName"]
    .astype(str)
    .str.strip()
    .str.lower()
)

pubchem["DrugName_key"] = (
    pubchem["DrugName"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# ---------------------------------------
# Duplicate Checks
# ---------------------------------------

duplicate_drugs = pubchem[
    pubchem["DrugName_key"].duplicated(keep=False)
]

duplicate_cids = pubchem[
    pubchem["CID"].duplicated(keep=False)
]

# ---------------------------------------
# Missing Values
# ---------------------------------------

missing_summary = pubchem[required_columns].isna().sum()

# ---------------------------------------
# Numeric Validation
# ---------------------------------------

numeric_columns = [
    "CID",
    "MolecularWeight",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount"
]

numeric_report = {}

for column in numeric_columns:

    numeric_report[column] = (
        pd.to_numeric(
            pubchem[column],
            errors="coerce"
        ).isna().sum()
    )

# ---------------------------------------
# Find Missing Drugs
# ---------------------------------------

pubchem_names = set(pubchem["DrugName_key"])

missing_drugs = master[
    ~master["DrugName_key"].isin(pubchem_names)
].copy()

missing_drugs = missing_drugs[
    ["DrugID", "DrugName"]
]

missing_drugs.to_csv(
    MISSING_FILE,
    index=False
)

# ---------------------------------------
# Validation Report
# ---------------------------------------

report = []

report.append({
    "Check": "Total master drugs",
    "Value": len(master)
})

report.append({
    "Check": "Total PubChem records",
    "Value": len(pubchem)
})

report.append({
    "Check": "Unique PubChem drugs",
    "Value": pubchem["DrugName_key"].nunique()
})

report.append({
    "Check": "Duplicate drug names",
    "Value": len(duplicate_drugs)
})

report.append({
    "Check": "Duplicate CIDs",
    "Value": len(duplicate_cids)
})

report.append({
    "Check": "Missing drugs from PubChem",
    "Value": len(missing_drugs)
})

for column in required_columns:

    report.append({
        "Check": f"Missing {column}",
        "Value": int(pubchem[column].isna().sum())
    })

validation_df = pd.DataFrame(report)

validation_df.to_csv(
    VALIDATION_FILE,
    index=False
)

# ---------------------------------------
# Print Results
# ---------------------------------------

print("=" * 65)
print("PubChem Data Validation Completed ✅")
print("=" * 65)

print("\nMaster Drugs :", len(master))
print("PubChem Records :", len(pubchem))
print(
    "Unique PubChem Drugs :",
    pubchem["DrugName_key"].nunique()
)

print(
    "Duplicate Drug Names :",
    len(duplicate_drugs)
)

print(
    "Duplicate CIDs :",
    len(duplicate_cids)
)

print(
    "Missing Drugs :",
    len(missing_drugs)
)

print("\nMissing Values:")
print(missing_summary)

print("\nFiles Created:")
print("✓", VALIDATION_FILE)
print("✓", MISSING_FILE)

# ---------------------------------------
# Remove Temporary Columns
# ---------------------------------------

master.drop(
    columns=["DrugName_key"],
    inplace=True
)

pubchem.drop(
    columns=["DrugName_key"],
    inplace=True
)