import os
import pandas as pd

# ============================================================
# FILES
# ============================================================

MASTER_FILE = "datasets/processed/master_drug_list.csv"
PUBCHEM_FILE = "datasets/processed/pubchem_data_result.csv"
RECOVERED_FILE = "datasets/processed/pubchem_recovered.csv"

OUTPUT_FILE = "datasets/final/master_drug_table.csv"

# ============================================================
# LOAD
# ============================================================

master = pd.read_csv(MASTER_FILE)
pubchem = pd.read_csv(PUBCHEM_FILE)
recovered = pd.read_csv(RECOVERED_FILE)

# ============================================================
# NORMALIZE NAMES
# ============================================================

def normalize(x):
    return str(x).strip().lower()

master["DrugName_key"] = master["DrugName"].apply(normalize)
pubchem["DrugName_key"] = pubchem["DrugName"].apply(normalize)
recovered["OriginalDrugName_key"] = (
    recovered["OriginalDrugName"].apply(normalize)
)

# ============================================================
# COMBINE PUBCHEM DATA
# ============================================================

pubchem["Source"] = "PubChem"
recovered["DrugName_key"] = recovered["OriginalDrugName_key"]
recovered["Source"] = "PubChem-Recovered"

# Keep same feature columns
columns = [
    "DrugName_key",
    "CID",
    "ConnectivitySMILES",
    "MolecularWeight",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount",
    "Source"
]

pubchem = pubchem[columns]
recovered = recovered[columns]

combined = pd.concat(
    [pubchem, recovered],
    ignore_index=True
)

# Remove duplicate drug mappings
combined = combined.drop_duplicates(
    subset=["DrugName_key"],
    keep="first"
)

# ============================================================
# MERGE WITH MASTER DRUG LIST
# ============================================================

final = master.merge(
    combined,
    on="DrugName_key",
    how="left"
)

# ============================================================
# STATUS
# ============================================================

final["PubChemStatus"] = final["CID"].apply(
    lambda x: "Available" if pd.notna(x)
    else "Unresolved"
)

# ============================================================
# REMOVE TEMP COLUMN
# ============================================================

final.drop(
    columns=["DrugName_key"],
    inplace=True
)

# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

# ============================================================
# SAVE
# ============================================================

final.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("Master Drug Table Created ✅")
print("=" * 70)

print("Total Drugs       :", len(final))
print(
    "PubChem Available :",
    (final["PubChemStatus"] == "Available").sum()
)
print(
    "Unresolved         :",
    (final["PubChemStatus"] == "Unresolved").sum()
)

print("\nOutput:")
print("✓", OUTPUT_FILE)

print("\nStatus:")
print(
    final["PubChemStatus"].value_counts()
)