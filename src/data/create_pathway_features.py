import pandas as pd

# ==========================================
# File paths
# ==========================================

drug_file = "datasets/final/master_drug_table.csv"

pathway_file = (
    "datasets/processed/drug_reactome_pathways.csv"
)

output_file = (
    "datasets/processed/drug_pathway_features.csv"
)


# ==========================================
# 1. Load drug table
# ==========================================

drugs = pd.read_csv(drug_file)

print("\n==============================")
print("LOADING DRUG DATA")
print("==============================")

print("Total drugs:", len(drugs))


# ==========================================
# 2. Load Reactome relationships
# ==========================================

pathways = pd.read_csv(pathway_file)

print("\n==============================")
print("LOADING PATHWAY DATA")
print("==============================")

print(
    "Drug-pathway relationships:",
    len(pathways)
)


# ==========================================
# 3. Create Drug × Pathway matrix
# ==========================================

pathway_matrix = pd.crosstab(
    pathways["DrugID"],
    pathways["Pathway_ID"]
)

# Convert counts to binary
pathway_matrix = (
    pathway_matrix > 0
).astype(int)


# ==========================================
# 4. Add all drugs
# ==========================================

pathway_matrix = pathway_matrix.reindex(
    drugs["DrugID"],
    fill_value=0
)


# ==========================================
# 5. Create pathway availability flag
# ==========================================

pathway_drug_ids = set(
    pathways["DrugID"]
)

pathway_matrix["PathwayAvailable"] = (
    pathway_matrix.index
    .isin(pathway_drug_ids)
    .astype(int)
)


# ==========================================
# 6. Add DrugID and DrugName
# ==========================================

pathway_matrix = (
    pathway_matrix
    .reset_index()
    .rename(columns={"index": "DrugID"})
)

pathway_matrix = pathway_matrix.merge(
    drugs[["DrugID", "DrugName"]],
    on="DrugID",
    how="left"
)


# ==========================================
# 7. Reorder columns
# ==========================================

first_columns = [
    "DrugID",
    "DrugName",
    "PathwayAvailable"
]

pathway_columns = [
    col
    for col in pathway_matrix.columns
    if col not in first_columns
]

pathway_matrix = pathway_matrix[
    first_columns + pathway_columns
]


# ==========================================
# 8. Save
# ==========================================

pathway_matrix.to_csv(
    output_file,
    index=False
)


# ==========================================
# 9. Summary
# ==========================================

print("\n==============================")
print("PATHWAY FEATURES CREATED ✅")
print("==============================")

print(
    "Number of drugs:",
    pathway_matrix.shape[0]
)

print(
    "Number of pathway features:",
    len(pathway_columns)
)

print(
    "Feature matrix shape:",
    pathway_matrix.shape
)

print(
    "Drugs with pathway data:",
    pathway_matrix[
        "PathwayAvailable"
    ].sum()
)

print(
    "Drugs without pathway data:",
    (
        pathway_matrix[
            "PathwayAvailable"
        ] == 0
    ).sum()
)

print("\nSaved:")
print(output_file)

print("\nPreview:")
print(
    pathway_matrix.iloc[:, :10]
    .head()
)