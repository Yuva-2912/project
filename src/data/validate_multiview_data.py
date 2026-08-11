import pandas as pd
import os

# ==========================================
# File paths
# ==========================================

files = {
    "Master Drug Table":
        "datasets/final/master_drug_table.csv",

    "Pathway Features":
        "datasets/processed/drug_pathway_features.csv",

    "SMILES Features":
        "datasets/processed/drug_smiles.csv",

    "Graph Edges":
        "datasets/final/graph_edges.csv"
}


# ==========================================
# Load and inspect
# ==========================================

print("\n==============================")
print("MULTI-VIEW DATA VALIDATION")
print("==============================")

dataframes = {}

for name, path in files.items():

    print("\n------------------------------")
    print(name)
    print("------------------------------")

    if not os.path.exists(path):
        print("❌ FILE NOT FOUND")
        print(path)
        continue

    df = pd.read_csv(path)

    dataframes[name] = df

    print("Shape:", df.shape)

    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 3 rows:")
    print(df.head(3))


# ==========================================
# Check DrugID alignment
# ==========================================

print("\n==============================")
print("DRUG ID ALIGNMENT")
print("==============================")

if (
    "Master Drug Table" in dataframes
    and "Pathway Features" in dataframes
):

    master_ids = set(
        dataframes["Master Drug Table"]["DrugID"]
    )

    pathway_ids = set(
        dataframes["Pathway Features"]["DrugID"]
    )

    print(
        "Master Drug IDs:",
        len(master_ids)
    )

    print(
        "Pathway Drug IDs:",
        len(pathway_ids)
    )

    print(
        "IDs missing from pathway:",
        len(master_ids - pathway_ids)
    )

    print(
        "Extra pathway IDs:",
        len(pathway_ids - master_ids)
    )


# ==========================================
# Check duplicates
# ==========================================

print("\n==============================")
print("DUPLICATE CHECK")
print("==============================")

for name, df in dataframes.items():

    if "DrugID" in df.columns:

        duplicates = df["DrugID"].duplicated().sum()

        print(
            f"{name}: {duplicates} duplicate DrugIDs"
        )


# ==========================================
# Missing values
# ==========================================

print("\n==============================")
print("MISSING VALUES")
print("==============================")

for name, df in dataframes.items():

    print(
        f"{name}:",
        int(df.isna().sum().sum()),
        "missing values"
    )


print("\n==============================")
print("VALIDATION FINISHED")
print("==============================")