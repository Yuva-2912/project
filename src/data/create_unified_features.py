import os
import pandas as pd
import numpy as np

# ============================================================
# PATHS
# ============================================================

MASTER = "datasets/final/master_drug_table.csv"

FILES = {
    "side_effects": "datasets/processed/drug_side_effects_recovered.csv",
    "targets": "datasets/processed/drug_targets.csv",
    "transporters": "datasets/processed/drug_transporters.csv",
    "mechanisms": "datasets/processed/drug_mechanisms.csv",
    "pathway_features": "datasets/processed/drug_pathway_features.csv",
    "reactome": "datasets/processed/drug_reactome_pathways.csv",
    "chebi": "datasets/processed/drug_chebi_mapping.csv",
    "smiles": "datasets/processed/drug_smiles.csv",
}

OUTPUT = "datasets/final/unified_drug_features.csv"

os.makedirs("datasets/final", exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def load_csv(path, name):
    if not os.path.exists(path):
        print(f"[WARNING] Missing: {path}")
        return None

    df = pd.read_csv(path, low_memory=False)

    print(f"{name}: {df.shape}")
    print(f"Columns: {list(df.columns)[:10]}")

    return df


def normalize_id(df):
    """
    Make sure DrugID is numeric where possible.
    """
    if df is None or "DrugID" not in df.columns:
        return df

    df["DrugID"] = pd.to_numeric(df["DrugID"], errors="coerce")
    df = df.dropna(subset=["DrugID"])
    df["DrugID"] = df["DrugID"].astype(int)

    return df


# ============================================================
# LOAD MASTER
# ============================================================

print("=" * 70)
print("UNIFIED DRUG FEATURE CREATION")
print("=" * 70)

master = load_csv(MASTER, "MASTER DRUG TABLE")

if master is None:
    raise FileNotFoundError(MASTER)

master = normalize_id(master)

print("\nMaster drugs:", len(master))
print("Master columns:", list(master.columns))


# ============================================================
# SELECT MASTER MOLECULAR FEATURES
# ============================================================

molecular_columns = [
    "DrugID",
    "DrugName",
    "CID",
    "MolecularWeight",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount",
]

available_molecular = [
    c for c in molecular_columns
    if c in master.columns
]

features = master[available_molecular].copy()


# ============================================================
# SIDE EFFECT FEATURES
# ============================================================

print("\n" + "-" * 70)
print("SIDE EFFECT FEATURES")
print("-" * 70)

side = load_csv(FILES["side_effects"], "Side effects")

if side is not None and "DrugID" in side.columns:

    side = normalize_id(side)

    side_count = (
        side.groupby("DrugID")
        .size()
        .reset_index(name="SideEffectCount")
    )

    side_unique = (
        side.groupby("DrugID")["SideEffect"]
        .nunique()
        .reset_index(name="UniqueSideEffectCount")
    )

    side_features = side_count.merge(
        side_unique,
        on="DrugID",
        how="outer"
    )

    features = features.merge(
        side_features,
        on="DrugID",
        how="left"
    )


# ============================================================
# TARGET FEATURES
# ============================================================

print("\n" + "-" * 70)
print("TARGET FEATURES")
print("-" * 70)

targets = load_csv(FILES["targets"], "Targets")

if targets is not None and "DrugID" in targets.columns:

    targets = normalize_id(targets)

    target_features = (
        targets.groupby("DrugID")
        .agg(
            TargetCount=("Target ID", "nunique")
            if "Target ID" in targets.columns
            else ("DrugID", "size"),
            TargetGeneCount=("Target Gene Symbol", "nunique")
            if "Target Gene Symbol" in targets.columns
            else ("DrugID", "size"),
        )
        .reset_index()
    )

    features = features.merge(
        target_features,
        on="DrugID",
        how="left"
    )


# ============================================================
# TRANSPORTER FEATURES
# ============================================================

print("\n" + "-" * 70)
print("TRANSPORTER FEATURES")
print("-" * 70)

transporters = load_csv(FILES["transporters"], "Transporters")

if transporters is not None:

    # Transporter dataset currently uses Ligand ID,
    # so map Ligand ID -> DrugID where possible.

    if "Ligand ID" in transporters.columns:

        transporters["DrugID"] = pd.to_numeric(
            transporters["Ligand ID"],
            errors="coerce"
        )

        transporters = transporters.dropna(subset=["DrugID"])
        transporters["DrugID"] = transporters["DrugID"].astype(int)

        transporter_features = (
            transporters.groupby("DrugID")
            .size()
            .reset_index(name="TransporterCount")
        )

        features = features.merge(
            transporter_features,
            on="DrugID",
            how="left"
        )

    else:
        print("[WARNING] Ligand ID not found.")


# ============================================================
# MECHANISM FEATURES
# ============================================================

print("\n" + "-" * 70)
print("MECHANISM FEATURES")
print("-" * 70)

mechanisms = load_csv(FILES["mechanisms"], "Mechanisms")

if mechanisms is not None:

    if "Ligand ID" in mechanisms.columns:

        mechanisms["DrugID"] = pd.to_numeric(
            mechanisms["Ligand ID"],
            errors="coerce"
        )

        mechanisms = mechanisms.dropna(subset=["DrugID"])
        mechanisms["DrugID"] = mechanisms["DrugID"].astype(int)

        mechanism_features = (
            mechanisms.groupby("DrugID")
            .size()
            .reset_index(name="MechanismCount")
        )

        features = features.merge(
            mechanism_features,
            on="DrugID",
            how="left"
        )

    else:
        print("[WARNING] Ligand ID not found.")


# ============================================================
# CHEBI FEATURES
# ============================================================

print("\n" + "-" * 70)
print("ChEBI FEATURES")
print("-" * 70)

chebi = load_csv(FILES["chebi"], "ChEBI")

if chebi is not None and "DrugID" in chebi.columns:

    chebi = normalize_id(chebi)

    chebi_features = (
        chebi.groupby("DrugID")
        .size()
        .reset_index(name="ChEBICount")
    )

    features = features.merge(
        chebi_features,
        on="DrugID",
        how="left"
    )


# ============================================================
# REACTOME PATHWAY FEATURES
# ============================================================

print("\n" + "-" * 70)
print("REACTOME PATHWAY FEATURES")
print("-" * 70)

reactome = load_csv(FILES["reactome"], "Reactome")

if reactome is not None and "DrugID" in reactome.columns:

    reactome = normalize_id(reactome)

    pathway_features = (
        reactome.groupby("DrugID")
        .agg(
            ReactomePathwayCount=("Pathway_ID", "nunique")
            if "Pathway_ID" in reactome.columns
            else ("DrugID", "size")
        )
        .reset_index()
    )

    features = features.merge(
        pathway_features,
        on="DrugID",
        how="left"
    )


# ============================================================
# PATHWAY FEATURE MATRIX
# ============================================================

print("\n" + "-" * 70)
print("PATHWAY FEATURE MATRIX")
print("-" * 70)

pathways = load_csv(
    FILES["pathway_features"],
    "Pathway features"
)

if pathways is not None and "DrugID" in pathways.columns:

    pathways = normalize_id(pathways)

    pathway_columns = [
        c for c in pathways.columns
        if c.startswith("R-HSA-")
    ]

    print("Reactome binary pathway columns:", len(pathway_columns))

    if pathway_columns:

        pathway_subset = pathways[
            ["DrugID"] + pathway_columns
        ].copy()

        # Avoid duplicate DrugID rows
        pathway_subset = (
            pathway_subset
            .groupby("DrugID")[pathway_columns]
            .max()
            .reset_index()
        )

        features = features.merge(
            pathway_subset,
            on="DrugID",
            how="left"
        )


# ============================================================
# SMILES AVAILABILITY
# ============================================================

print("\n" + "-" * 70)
print("SMILES FEATURES")
print("-" * 70)

smiles = load_csv(FILES["smiles"], "SMILES")

if smiles is not None and "DrugID" in smiles.columns:

    smiles = normalize_id(smiles)

    smiles["SMILESAvailable"] = (
        smiles["ConnectivitySMILES"]
        .notna()
        .astype(int)
        if "ConnectivitySMILES" in smiles.columns
        else 0
    )

    smiles_features = (
        smiles.groupby("DrugID")["SMILESAvailable"]
        .max()
        .reset_index()
    )

    features = features.merge(
        smiles_features,
        on="DrugID",
        how="left"
    )


# ============================================================
# REMOVE DUPLICATE DRUGS
# ============================================================

features = features.drop_duplicates(
    subset=["DrugID"]
).copy()


# ============================================================
# MISSING VALUE HANDLING
# ============================================================

count_columns = [
    "SideEffectCount",
    "UniqueSideEffectCount",
    "TargetCount",
    "TargetGeneCount",
    "TransporterCount",
    "MechanismCount",
    "ChEBICount",
    "ReactomePathwayCount",
    "SMILESAvailable",
]

for col in count_columns:
    if col in features.columns:
        features[col] = features[col].fillna(0)


# Molecular properties are kept as NaN for now.
# We will inspect them before choosing an imputation method.


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("UNIFIED FEATURE MATRIX")
print("=" * 70)

print("Shape:", features.shape)

print("\nColumns:")
for i, col in enumerate(features.columns, 1):
    print(f"{i:3}. {col}")


print("\nMissing values:")
missing = features.isna().sum()

missing = missing[missing > 0].sort_values(
    ascending=False
)

if len(missing) == 0:
    print("No missing values.")
else:
    print(missing)


print("\nMissing percentage:")

missing_percent = (
    features.isna().mean() * 100
).sort_values(ascending=False)

missing_percent = missing_percent[
    missing_percent > 0
]

if len(missing_percent) > 0:
    print(missing_percent)


# ============================================================
# SAVE
# ============================================================

features.to_csv(
    OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print("COMPLETED")
print("=" * 70)

print("Saved:", OUTPUT)
print("Rows:", len(features))
print("Columns:", len(features.columns))