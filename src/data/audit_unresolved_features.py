import pandas as pd

MASTER_FILE = "datasets/final/master_drug_table.csv"
CHEMICAL_FILE = "datasets/processed/chemical_features.csv"
UNRESOLVED_FILE = "datasets/processed/unresolved_drugs.csv"

master = pd.read_csv(MASTER_FILE)
chemical = pd.read_csv(CHEMICAL_FILE)

# Force missing values to remain identifiable
chemical = chemical.replace(["", "nan", "None"], pd.NA)

# Find unresolved drugs from master table
unresolved = master[
    master["PubChemStatus"].astype(str).str.lower().eq("unresolved")
].copy()

# Match their chemical feature records
audit = unresolved[["DrugID", "DrugName"]].merge(
    chemical,
    on=["DrugID", "DrugName"],
    how="left"
)

feature_columns = [
    "CID",
    "MolecularFormula",
    "MolecularWeight",
    "ExactMass",
    "MonoisotopicMass",
    "HeavyAtomCount",
    "FormalCharge",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount",
    "Complexity",
    "ConnectivitySMILES",
    "IsomericSMILES",
    "InChI",
    "InChIKey"
]

print("=" * 70)
print("UNRESOLVED DRUG FEATURE AUDIT")
print("=" * 70)

print(f"Total master drugs : {len(master)}")
print(f"Unresolved drugs   : {len(unresolved)}")

print("\nMissing feature counts:")
print("-" * 70)

for column in feature_columns:
    if column in audit.columns:
        missing = audit[column].isna().sum()
        available = len(audit) - missing
        print(f"{column:25} Available: {available:2}  Missing: {missing:2}")

# Save detailed audit
output = "datasets/processed/unresolved_feature_audit.csv"
audit.to_csv(output, index=False)

print("\nUnresolved drugs:")
print("-" * 70)

print(
    audit[
        ["DrugID", "DrugName"] +
        [c for c in feature_columns if c in audit.columns]
    ].to_string(index=False)
)

print("\nOutput:")
print(f"✓ {output}")

print("=" * 70)