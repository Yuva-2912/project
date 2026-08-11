import pandas as pd

# ==========================================
# Load datasets
# ==========================================

drug_df = pd.read_csv(
    "datasets/final/master_drug_table.csv"
)

chebi_df = pd.read_csv(
    "datasets/processed/drug_chebi_mapping.csv"
)

pathway_df = pd.read_csv(
    "datasets/processed/drug_reactome_pathways.csv"
)


# ==========================================
# Basic counts
# ==========================================

total_drugs = len(drug_df)

cid_drugs = drug_df["CID"].notna().sum()

chebi_drugs = chebi_df["ChEBI_ID"].notna().sum()

pathway_drugs = pathway_df["DrugID"].nunique()


# ==========================================
# Coverage
# ==========================================

chebi_coverage = (
    chebi_drugs / cid_drugs
) * 100

pathway_coverage = (
    pathway_drugs / chebi_drugs
) * 100


print("\n==============================")
print("PATHWAY COVERAGE ANALYSIS")
print("==============================")

print("Total drugs:", total_drugs)

print("Drugs with CID:", cid_drugs)

print("Drugs with ChEBI:", chebi_drugs)

print("Drugs with Reactome pathways:", pathway_drugs)

print(
    f"\nChEBI coverage: {chebi_coverage:.2f}%"
)

print(
    f"Reactome coverage among ChEBI drugs: "
    f"{pathway_coverage:.2f}%"
)


# ==========================================
# Pathway statistics
# ==========================================

print("\n==============================")
print("PATHWAY STATISTICS")
print("==============================")

print(
    "Unique pathways:",
    pathway_df["Pathway_ID"].nunique()
)

print(
    "Total drug-pathway relationships:",
    len(pathway_df)
)

print(
    "Average pathways per mapped drug:",
    round(
        len(pathway_df) /
        pathway_df["DrugID"].nunique(),
        2
    )
)


# ==========================================
# Most connected pathways
# ==========================================

pathway_counts = (
    pathway_df
    .groupby(
        ["Pathway_ID", "Pathway_Name"]
    )
    .size()
    .reset_index(name="DrugCount")
    .sort_values(
        "DrugCount",
        ascending=False
    )
)

print("\n==============================")
print("TOP 10 PATHWAYS")
print("==============================")

print(
    pathway_counts.head(10).to_string(
        index=False
    )
)