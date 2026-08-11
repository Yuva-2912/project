import os
import pandas as pd

# ============================================================
# COMPLETE DATASET COVERAGE AUDIT - V2
# ============================================================

print("=" * 70)
print("COMPLETE DATASET COVERAGE AUDIT - V2")
print("=" * 70)

FILES = {
    "Master": "datasets/final/master_drug_table.csv",
    "Chemical": "datasets/processed/chemical_features.csv",
    "Pathway": "datasets/processed/drug_pathway_features.csv",
    "SMILES": "datasets/final/smiles_features.csv",
    "SIDER": "datasets/processed/drug_side_effects.csv",
    "ChEBI": "datasets/processed/drug_chebi_mapping.csv",
    "Targets": "datasets/processed/drug_targets.csv",
    "Transporters": "datasets/processed/drug_transporters.csv",
    "Mechanism": "datasets/processed/drug_mechanisms.csv",
}

data = {}

# ============================================================
# LOAD DATASETS
# ============================================================

print("\n" + "=" * 70)
print("LOADING DATASETS")
print("=" * 70)

for name, path in FILES.items():

    if not os.path.exists(path):
        print(f"\n{name}: NOT FOUND")
        print(f"Path: {path}")
        continue

    try:
        df = pd.read_csv(path, low_memory=False)
        data[name] = df

        print(f"\n{name}")
        print(f"Shape   : {df.shape}")
        print(f"Columns : {list(df.columns)}")

    except Exception as e:
        print(f"\n{name}: ERROR")
        print(e)


# ============================================================
# MASTER
# ============================================================

if "Master" not in data:
    raise FileNotFoundError(
        "Master dataset could not be loaded."
    )

master = data["Master"]

if "DrugID" not in master.columns:
    raise ValueError(
        "Master dataset does not contain DrugID."
    )

master_ids = set(
    master["DrugID"].dropna().astype(int)
)

print("\n" + "=" * 70)
print("MASTER DATASET")
print("=" * 70)

print(f"Rows             : {len(master)}")
print(f"Unique DrugIDs   : {len(master_ids)}")
print(
    f"Duplicate DrugIDs: "
    f"{master['DrugID'].duplicated().sum()}"
)


# ============================================================
# GENERIC DRUGID COVERAGE
# ============================================================

def check_drug_id_dataset(name, df):

    print("\n" + "-" * 70)
    print(name)
    print("-" * 70)

    if "DrugID" not in df.columns:
        print("No DrugID column.")
        return

    ids = set(
        df["DrugID"].dropna().astype(int)
    )

    missing = master_ids - ids
    extra = ids - master_ids

    print(f"Rows              : {len(df)}")
    print(f"Unique DrugIDs     : {len(ids)}")
    print(f"Missing drugs      : {len(missing)}")
    print(f"Extra DrugIDs      : {len(extra)}")
    print(
        f"Duplicate DrugIDs  : "
        f"{df['DrugID'].duplicated().sum()}"
    )

    if missing:

        missing_df = master[
            master["DrugID"].isin(missing)
        ][["DrugID", "DrugName"]]

        print("\nMissing drugs:")
        print(
            missing_df.to_string(index=False)
        )

        os.makedirs(
            "datasets/processed/missing",
            exist_ok=True
        )

        missing_df.to_csv(
            f"datasets/processed/missing/"
            f"missing_{name.lower()}_drugs.csv",
            index=False
        )


# ============================================================
# CHECK DRUGID DATASETS
# ============================================================

for name in [
    "Chemical",
    "Pathway",
    "SMILES",
    "ChEBI",
    "Targets",
    "Transporters"
]:

    if name in data:
        check_drug_id_dataset(
            name,
            data[name]
        )


# ============================================================
# SIDER
# ============================================================

print("\n" + "=" * 70)
print("SIDER COVERAGE")
print("=" * 70)

if "SIDER" in data:

    sider = data["SIDER"]

    print(f"Rows: {len(sider)}")
    print(f"Columns: {list(sider.columns)}")

    if "DrugID" in sider.columns:

        sider_ids = set(
            sider["DrugID"].dropna().astype(int)
        )

        missing = master_ids - sider_ids

        print(f"\nMaster drugs       : {len(master_ids)}")
        print(f"SIDER DrugIDs      : {len(sider_ids)}")
        print(f"Missing SIDER      : {len(missing)}")

        if missing:

            missing_df = master[
                master["DrugID"].isin(missing)
            ][["DrugID", "DrugName"]]

            print("\nDrugs missing SIDER:")
            print(
                missing_df.to_string(index=False)
            )

            os.makedirs(
                "datasets/processed/missing",
                exist_ok=True
            )

            missing_df.to_csv(
                "datasets/processed/missing/"
                "missing_sider_drugs.csv",
                index=False
            )

    else:

        print(
            "\nWARNING: SIDER does not contain DrugID."
        )


# ============================================================
# CHEBI
# ============================================================

print("\n" + "=" * 70)
print("ChEBI COVERAGE")
print("=" * 70)

if "ChEBI" in data:

    chebi = data["ChEBI"]

    print(f"Rows: {len(chebi)}")
    print(f"Columns: {list(chebi.columns)}")

    if "DrugID" in chebi.columns:

        chebi_ids = set(
            chebi["DrugID"].dropna().astype(int)
        )

        missing = master_ids - chebi_ids

        print(f"\nMaster drugs       : {len(master_ids)}")
        print(f"ChEBI DrugIDs      : {len(chebi_ids)}")
        print(f"Missing ChEBI      : {len(missing)}")

        if missing:

            missing_df = master[
                master["DrugID"].isin(missing)
            ][["DrugID", "DrugName"]]

            print("\nDrugs missing ChEBI:")
            print(
                missing_df.to_string(index=False)
            )

            os.makedirs(
                "datasets/processed/missing",
                exist_ok=True
            )

            missing_df.to_csv(
                "datasets/processed/missing/"
                "missing_chebi_drugs.csv",
                index=False
            )


# ============================================================
# MECHANISM
# ============================================================

print("\n" + "=" * 70)
print("MECHANISM DATASET")
print("=" * 70)

if "Mechanism" in data:

    mechanism = data["Mechanism"]

    print(f"Rows: {len(mechanism)}")
    print(
        f"Unique Ligand IDs: "
        f"{mechanism['Ligand ID'].nunique()}"
        if "Ligand ID" in mechanism.columns
        else "Ligand ID column not found"
    )

    print(
        f"Unique Ligands: "
        f"{mechanism['Ligand'].nunique()}"
        if "Ligand" in mechanism.columns
        else "Ligand column not found"
    )

    print("\nFirst 10 mechanism records:")

    print(
        mechanism[
            [
                c for c in [
                    "Ligand ID",
                    "Ligand",
                    "Target",
                    "Target Gene Symbol",
                    "Target UniProt ID",
                    "Action"
                ]
                if c in mechanism.columns
            ]
        ].head(10).to_string(index=False)
    )

    print(
        "\nIMPORTANT:"
        "\nMechanism dataset currently has no DrugID."
        "\nWe must map it to DrugID before merging."
    )


# ============================================================
# MASTER NULL VALUES
# ============================================================

print("\n" + "=" * 70)
print("MASTER NULL VALUES")
print("=" * 70)

null_counts = master.isna().sum()

null_counts = null_counts[
    null_counts > 0
].sort_values(
    ascending=False
)

print(null_counts)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("COVERAGE SUMMARY")
print("=" * 70)

summary = []

for name, df in data.items():

    if "DrugID" not in df.columns:
        continue

    ids = set(
        df["DrugID"].dropna().astype(int)
    )

    missing = master_ids - ids

    coverage = (
        len(ids & master_ids)
        / len(master_ids)
        * 100
    )

    summary.append({
        "Dataset": name,
        "Rows": len(df),
        "Unique_DrugIDs": len(ids),
        "Coverage_%": round(coverage, 2),
        "Missing_Drugs": len(missing),
        "Duplicate_DrugIDs":
            int(df["DrugID"].duplicated().sum())
    })

summary_df = pd.DataFrame(summary)

print(
    summary_df.to_string(index=False)
)

os.makedirs(
    "datasets/processed/audit",
    exist_ok=True
)

summary_df.to_csv(
    "datasets/processed/audit/"
    "complete_feature_coverage_summary.csv",
    index=False
)

print(
    "\nSaved:"
    "\ndatasets/processed/audit/"
    "complete_feature_coverage_summary.csv"
)

print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("=" * 70)