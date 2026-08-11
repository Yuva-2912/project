import pandas as pd
from pathlib import Path

print("=" * 60)
print("MISSING MULTI-VIEW FEATURE AUDIT")
print("=" * 60)

# ============================================================
# PATHS
# ============================================================

MASTER_PATH = Path("datasets/final/master_drug_table.csv")
SMILES_PATH = Path("datasets/processed/drug_smiles.csv")

OUTPUT_DIR = Path("datasets/processed")

MISSING_SMILES_PATH = OUTPUT_DIR / "missing_smiles_drugs.csv"
MASTER_NULLS_PATH = OUTPUT_DIR / "master_missing_values.csv"

# ============================================================
# LOAD
# ============================================================

master = pd.read_csv(MASTER_PATH)
smiles = pd.read_csv(SMILES_PATH)

print("\nMaster shape:", master.shape)
print("Master columns:")
print(master.columns.tolist())

print("\nSMILES shape:", smiles.shape)
print("SMILES columns:")
print(smiles.columns.tolist())

# ============================================================
# SMILES COVERAGE
# ============================================================

print("\n" + "-" * 60)
print("SMILES COVERAGE")
print("-" * 60)

master_ids = set(master["DrugID"])
smiles_ids = set(smiles["DrugID"])

missing_smiles_ids = sorted(master_ids - smiles_ids)

print("Master DrugIDs:", len(master_ids))
print("SMILES DrugIDs:", len(smiles_ids))
print("Missing SMILES:", len(missing_smiles_ids))

if missing_smiles_ids:

    missing_smiles = master[
        master["DrugID"].isin(missing_smiles_ids)
    ].copy()

    display_columns = [
        col for col in [
            "DrugID",
            "DrugName",
            "CID",
            "ConnectivitySMILES",
            "PubChemStatus"
        ]
        if col in missing_smiles.columns
    ]

    print("\nDrugs missing from SMILES dataset:")
    print(
        missing_smiles[display_columns].to_string(index=False)
    )

    missing_smiles.to_csv(
        MISSING_SMILES_PATH,
        index=False
    )

    print("\nSaved:")
    print(MISSING_SMILES_PATH)

else:
    print("No missing SMILES drugs.")

# ============================================================
# MASTER SMILES NULL CHECK
# ============================================================

print("\n" + "-" * 60)
print("MASTER SMILES NULL CHECK")
print("-" * 60)

if "ConnectivitySMILES" in master.columns:

    null_smiles = master[
        master["ConnectivitySMILES"].isna()
        |
        (
            master["ConnectivitySMILES"]
            .astype(str)
            .str.strip()
            .eq("")
        )
    ]

    print(
        "Missing ConnectivitySMILES in master:",
        len(null_smiles)
    )

    if len(null_smiles) > 0:

        display_columns = [
            col for col in [
                "DrugID",
                "DrugName",
                "CID",
                "PubChemStatus"
            ]
            if col in null_smiles.columns
        ]

        print(
            null_smiles[display_columns].to_string(index=False)
        )

# ============================================================
# MASTER MISSING VALUES
# ============================================================

print("\n" + "-" * 60)
print("MASTER MISSING VALUES BY COLUMN")
print("-" * 60)

null_counts = master.isna().sum()

null_counts = null_counts[
    null_counts > 0
].sort_values(ascending=False)

if len(null_counts) == 0:

    print("No missing values in master table.")

else:

    print(null_counts.to_string())

    rows_with_nulls = master[
        master.isna().any(axis=1)
    ].copy()

    print(
        "\nRows containing missing values:",
        len(rows_with_nulls)
    )

    rows_with_nulls.to_csv(
        MASTER_NULLS_PATH,
        index=False
    )

    print("\nSaved:")
    print(MASTER_NULLS_PATH)

# ============================================================
# DUPLICATES
# ============================================================

print("\n" + "-" * 60)
print("DUPLICATE CHECK")
print("-" * 60)

print(
    "Master duplicate DrugIDs:",
    master["DrugID"].duplicated().sum()
)

print(
    "SMILES duplicate DrugIDs:",
    smiles["DrugID"].duplicated().sum()
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("AUDIT SUMMARY")
print("=" * 60)

print(f"Master drugs             : {len(master):,}")
print(f"SMILES drugs             : {len(smiles):,}")
print(f"Missing SMILES drugs     : {len(missing_smiles_ids):,}")
print(
    f"Master rows with NULL    : "
    f"{master.isna().any(axis=1).sum():,}"
)
print(
    f"Master total NULL values : "
    f"{master.isna().sum().sum():,}"
)

print("\nAudit completed.")