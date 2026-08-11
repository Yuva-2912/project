import pandas as pd

base_path = "datasets/raw/reactome/"


# ==========================================
# 1. Reactome Pathways
# ==========================================

pathways_file = base_path + "ReactomePathways.txt"

pathways = pd.read_csv(
    pathways_file,
    sep="\t",
    header=None
)

print("\n==============================")
print("REACTOME PATHWAYS")
print("==============================")

print("Shape:", pathways.shape)
print("\nFirst 5 rows:")
print(pathways.head())

print("\nColumns:")
print(pathways.columns.tolist())


# ==========================================
# 2. Reactome Pathway Relationships
# ==========================================

relation_file = base_path + "ReactomePathwaysRelation.txt"

relations = pd.read_csv(
    relation_file,
    sep="\t",
    header=None
)

print("\n==============================")
print("PATHWAY RELATIONSHIPS")
print("==============================")

print("Shape:", relations.shape)
print("\nFirst 5 rows:")
print(relations.head())

print("\nColumns:")
print(relations.columns.tolist())


# ==========================================
# 3. ChEBI → Reactome Mapping
# ==========================================

chebi_file = base_path + "ChEBI2Reactome_All_Levels.txt"

chebi = pd.read_csv(
    chebi_file,
    sep="\t",
    header=None
)

print("\n==============================")
print("CHEBI → REACTOME")
print("==============================")

print("Shape:", chebi.shape)
print("\nFirst 5 rows:")
print(chebi.head())

print("\nColumns:")
print(chebi.columns.tolist())

print("\n==============================")
print("CHEBI COLUMN DETAILS")
print("==============================")

for i in range(chebi.shape[1]):
    print(f"\nColumn {i}:")
    print(chebi.iloc[:, i].head(10).tolist())