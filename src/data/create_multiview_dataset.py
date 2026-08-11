import os
import numpy as np
import pandas as pd

print("=" * 60)
print("CREATING FINAL MULTI-VIEW DATASET")
print("=" * 60)

# ============================================================
# PATHS
# ============================================================

MASTER_PATH = "datasets/processed/master_drug_list.csv"
CHEMICAL_PATH = "datasets/processed/chemical_features.csv"
PATHWAY_PATH = "datasets/processed/drug_pathway_features.csv"
SMILES_PATH = "datasets/final/smiles_features.csv"
GRAPH_PATH = "datasets/final/graph_edges.csv"

OUTPUT_DIR = "datasets/final"

# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading datasets...")

master = pd.read_csv(MASTER_PATH)
chemical = pd.read_csv(CHEMICAL_PATH)
pathway = pd.read_csv(PATHWAY_PATH)
smiles = pd.read_csv(SMILES_PATH)
graph = pd.read_csv(GRAPH_PATH)

print(f"Master   : {master.shape}")
print(f"Chemical : {chemical.shape}")
print(f"Pathway  : {pathway.shape}")
print(f"SMILES   : {smiles.shape}")
print(f"Graph    : {graph.shape}")

# ============================================================
# SORT BY DRUG ID
# ============================================================

master = master.sort_values("DrugID").reset_index(drop=True)
chemical = chemical.sort_values("DrugID").reset_index(drop=True)
pathway = pathway.sort_values("DrugID").reset_index(drop=True)
smiles = smiles.sort_values("DrugID").reset_index(drop=True)

# ============================================================
# DRUG ID ALIGNMENT
# ============================================================

master_ids = master["DrugID"].to_numpy()

for name, df in [
    ("Chemical", chemical),
    ("Pathway", pathway),
    ("SMILES", smiles)
]:
    ids = df["DrugID"].to_numpy()

    if not np.array_equal(master_ids, ids):
        raise ValueError(
            f"{name} DrugIDs are not aligned with master!"
        )

print("\nDrug ID alignment: OK")

# ============================================================
# REMOVE NON-FEATURE COLUMNS
# ============================================================

chemical_feature_cols = [
    c for c in chemical.columns
    if c not in ["DrugID", "DrugName"]
]

pathway_feature_cols = [
    c for c in pathway.columns
    if c not in ["DrugID", "DrugName", "PathwayAvailable"]
]

smiles_feature_cols = [
    c for c in smiles.columns
    if c.startswith("SMILES_")
]

# ============================================================
# CONVERT FEATURES TO NUMERIC
# ============================================================

chemical_matrix = (
    chemical[chemical_feature_cols]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(0)
    .to_numpy(dtype=np.float32)
)

pathway_matrix = (
    pathway[pathway_feature_cols]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(0)
    .to_numpy(dtype=np.float32)
)

smiles_matrix = (
    smiles[smiles_feature_cols]
    .apply(pd.to_numeric, errors="coerce")
    .fillna(0)
    .to_numpy(dtype=np.int64)
)

smiles_available = (
    smiles["SMILESAvailable"]
    .to_numpy(dtype=np.int64)
)

smiles_missing = (
    smiles["SMILESMissing"]
    .to_numpy(dtype=np.int64)
)

# ============================================================
# GRAPH EDGES
# ============================================================

edge_index = graph[
    ["DrugID_1", "DrugID_2"]
].to_numpy(dtype=np.int64).T

# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("MULTI-VIEW SHAPES")
print("=" * 60)

print(f"Drug IDs          : {master_ids.shape}")
print(f"Chemical features : {chemical_matrix.shape}")
print(f"Pathway features  : {pathway_matrix.shape}")
print(f"SMILES sequences  : {smiles_matrix.shape}")
print(f"Graph edges       : {edge_index.shape}")

print("\nExpected number of drugs:", len(master_ids))

if chemical_matrix.shape[0] != 3170:
    raise ValueError("Chemical feature count mismatch!")

if pathway_matrix.shape[0] != 3170:
    raise ValueError("Pathway feature count mismatch!")

if smiles_matrix.shape[0] != 3170:
    raise ValueError("SMILES feature count mismatch!")

# ============================================================
# SAVE AS NPZ
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

output_path = os.path.join(
    OUTPUT_DIR,
    "multiview_dataset.npz"
)

np.savez_compressed(
    output_path,

    # Identity
    drug_ids=master_ids,

    # View 1: chemical
    chemical_features=chemical_matrix,

    # View 2: pathway
    pathway_features=pathway_matrix,

    # View 3: SMILES sequence
    smiles_sequences=smiles_matrix,

    # SMILES availability
    smiles_available=smiles_available,
    smiles_missing=smiles_missing,

    # Graph
    edge_index=edge_index
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FINAL MULTI-VIEW DATASET CREATED")
print("=" * 60)

print(f"Drugs              : {len(master_ids)}")
print(f"Chemical dimension  : {chemical_matrix.shape[1]}")
print(f"Pathway dimension   : {pathway_matrix.shape[1]}")
print(f"SMILES length       : {smiles_matrix.shape[1]}")
print(f"Graph edges         : {edge_index.shape[1]}")
print(f"Missing SMILES      : {smiles_missing.sum()}")

print("\nSaved:")
print(output_path)

print("\nViews:")
print("1. Chemical molecular features")
print("2. Reactome pathway features")
print("3. SMILES sequence features")
print("4. Drug interaction graph")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)