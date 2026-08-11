import pandas as pd
import os

MASTER_FILE = "datasets/final/master_drug_table.csv"
CHEMICAL_FILE = "datasets/processed/chemical_features.csv"
OUTPUT_FILE = "datasets/processed/chemical_features.csv"

print("=" * 70)
print("RECOVERING SMILES FROM EXISTING DATA")
print("=" * 70)

master = pd.read_csv(MASTER_FILE)
chemical = pd.read_csv(CHEMICAL_FILE)

print(f"Master Drug Table : {master.shape}")
print(f"Chemical Features : {chemical.shape}")

# ---------------------------------------------------------
# Force SMILES columns to string/object
# ---------------------------------------------------------

chemical["ConnectivitySMILES"] = (
    chemical["ConnectivitySMILES"]
    .astype("object")
)

chemical["IsomericSMILES"] = (
    chemical["IsomericSMILES"]
    .astype("object")
)

master["ConnectivitySMILES"] = (
    master["ConnectivitySMILES"]
    .astype("object")
)

# ---------------------------------------------------------
# Clean master SMILES
# ---------------------------------------------------------

master["ConnectivitySMILES"] = (
    master["ConnectivitySMILES"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# Create DrugID → SMILES lookup
smiles_map = dict(
    zip(
        master["DrugID"],
        master["ConnectivitySMILES"]
    )
)

# ---------------------------------------------------------
# Count before recovery
# ---------------------------------------------------------

before = (
    chemical["ConnectivitySMILES"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
).sum()

recovered = 0

# ---------------------------------------------------------
# Recover SMILES
# ---------------------------------------------------------

for index in chemical.index:

    current = str(
        chemical.at[index, "ConnectivitySMILES"]
    ).strip()

    if current == "" or current.lower() == "nan":

        drug_id = chemical.at[index, "DrugID"]

        smiles = smiles_map.get(drug_id, "")

        if smiles:
            chemical.at[
                index,
                "ConnectivitySMILES"
            ] = smiles

            recovered += 1

# ---------------------------------------------------------
# Count after recovery
# ---------------------------------------------------------

after = (
    chemical["ConnectivitySMILES"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
).sum()

isomeric_count = (
    chemical["IsomericSMILES"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
).sum()

# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

chemical.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 70)
print("SMILES RECOVERY COMPLETED")
print("=" * 70)

print(f"ConnectivitySMILES before : {before}")
print(f"Recovered from master     : {recovered}")
print(f"ConnectivitySMILES after  : {after}")
print(f"IsomericSMILES available  : {isomeric_count}")

print()
print("Output:")
print(f"✓ {OUTPUT_FILE}")