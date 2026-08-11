import pandas as pd

file = "datasets/processed/drug_pathway_features.csv"

df = pd.read_csv(file)

print("\n==============================")
print("PATHWAY FEATURE VALIDATION")
print("==============================")

print("Shape:", df.shape)

print("\nDuplicate DrugIDs:")
print(df["DrugID"].duplicated().sum())

print("\nPathwayAvailable values:")
print(df["PathwayAvailable"].value_counts().sort_index())

# Pathway columns
pathway_columns = [
    col for col in df.columns
    if col.startswith("R-")
]

print("\nNumber of pathway columns:")
print(len(pathway_columns))

# Check values
unique_values = pd.unique(
    df[pathway_columns].values.ravel()
)

print("\nUnique pathway feature values:")
print(sorted(unique_values.tolist()))

# Total pathway assignments
total_assignments = df[pathway_columns].sum().sum()

print("\nTotal pathway assignments:")
print(int(total_assignments))

# Drugs with at least one pathway
drugs_with_pathways = (
    (df[pathway_columns].sum(axis=1) > 0).sum()
)

print("\nDrugs with at least one pathway:")
print(int(drugs_with_pathways))

# Missing values
print("\nMissing values in pathway features:")
print(
    df[pathway_columns]
    .isna()
    .sum()
    .sum()
)

print("\n==============================")
print("VALIDATION COMPLETED")
print("==============================")