import pandas as pd

# ==========================================
# File paths
# ==========================================

chebi_file = "datasets/processed/drug_chebi_mapping.csv"

reactome_mapping_file = (
    "datasets/raw/reactome/ChEBI2Reactome_All_Levels.txt"
)

output_file = (
    "datasets/processed/drug_reactome_pathways.csv"
)


# ==========================================
# 1. Load Drug → ChEBI mapping
# ==========================================

drug_chebi = pd.read_csv(chebi_file)

print("\n==============================")
print("DRUG → CHEBI")
print("==============================")

print("Rows:", len(drug_chebi))

drug_chebi = drug_chebi[
    drug_chebi["ChEBI_ID"].notna()
].copy()

# Convert CHEBI:15365 → 15365
drug_chebi["ChEBI_ID_Number"] = (
    drug_chebi["ChEBI_ID"]
    .astype(str)
    .str.replace("CHEBI:", "", regex=False)
)

drug_chebi["ChEBI_ID_Number"] = pd.to_numeric(
    drug_chebi["ChEBI_ID_Number"],
    errors="coerce"
)

print("Drugs with ChEBI:", len(drug_chebi))


# ==========================================
# 2. Load Reactome ChEBI mapping
# ==========================================

reactome = pd.read_csv(
    reactome_mapping_file,
    sep="\t",
    header=None,
    names=[
        "ChEBI_ID",
        "Pathway_ID",
        "Pathway_URL",
        "Pathway_Name",
        "Evidence",
        "Species"
    ]
)

print("\n==============================")
print("REACTOME")
print("==============================")

print("Total Reactome mappings:", len(reactome))


# ==========================================
# 3. Keep Homo sapiens pathways
# ==========================================

reactome_human = reactome[
    reactome["Species"] == "Homo sapiens"
].copy()

print(
    "Human Reactome mappings:",
    len(reactome_human)
)


# ==========================================
# 4. Rename Reactome ChEBI column
# ==========================================

reactome_human = reactome_human.rename(
    columns={
        "ChEBI_ID": "ChEBI_ID_Number"
    }
)


# ==========================================
# 5. Merge Drug → ChEBI → Reactome
# ==========================================

merged = drug_chebi.merge(
    reactome_human,
    on="ChEBI_ID_Number",
    how="inner"
)


# ==========================================
# 6. Select required columns
# ==========================================

result = merged[
    [
        "DrugID",
        "DrugName",
        "CID",
        "ChEBI_ID",
        "Pathway_ID",
        "Pathway_Name",
        "Evidence",
        "Species"
    ]
].drop_duplicates()


# ==========================================
# 7. Save
# ==========================================

result.to_csv(
    output_file,
    index=False
)


# ==========================================
# 8. Summary
# ==========================================

print("\n==============================")
print("DRUG → REACTOME MAPPING")
print("==============================")

print(
    "Unique drugs mapped:",
    result["DrugID"].nunique()
)

print(
    "Unique pathways:",
    result["Pathway_ID"].nunique()
)

print(
    "Total drug-pathway relationships:",
    len(result)
)

print("\nSaved:")
print(output_file)

print("\nPreview:")
print(result.head(10))