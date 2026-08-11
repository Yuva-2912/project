import pandas as pd

DDI_INPUT = "datasets/processed/ddi_unique_pairs.csv"
MASTER_INPUT = "datasets/final/master_drug_table.csv"
OUTPUT = "datasets/final/graph_edges.csv"

print("=" * 40)
print("CREATING GRAPH EDGES")
print("=" * 40)

ddi = pd.read_csv(DDI_INPUT)
master = pd.read_csv(MASTER_INPUT)

print("DDI shape:", ddi.shape)
print("Master shape:", master.shape)

# Create DrugName -> DrugID mapping
drug_map = master[["DrugID", "DrugName"]].copy()

drug_map["DrugName"] = (
    drug_map["DrugName"]
    .astype(str)
    .str.strip()
    .str.lower()
)

# Map drug1
ddi["drug1_clean"] = (
    ddi["drug1"]
    .astype(str)
    .str.strip()
    .str.lower()
)

ddi["drug2_clean"] = (
    ddi["drug2"]
    .astype(str)
    .str.strip()
    .str.lower()
)

ddi["DrugID_1"] = ddi["drug1_clean"].map(
    drug_map.set_index("DrugName")["DrugID"]
)

ddi["DrugID_2"] = ddi["drug2_clean"].map(
    drug_map.set_index("DrugName")["DrugID"]
)

print("\nMapping results:")
print("Total DDI pairs:", len(ddi))
print("Drug1 mapped:", ddi["DrugID_1"].notna().sum())
print("Drug2 mapped:", ddi["DrugID_2"].notna().sum())

# Keep only successfully mapped pairs
edges = ddi[[
    "DrugID_1",
    "DrugID_2"
]].dropna()

# Convert IDs to integers
edges["DrugID_1"] = edges["DrugID_1"].astype(int)
edges["DrugID_2"] = edges["DrugID_2"].astype(int)

# Remove duplicate edges
edges = edges.drop_duplicates()

# Remove self-loops
edges = edges[
    edges["DrugID_1"] != edges["DrugID_2"]
]

edges.to_csv(OUTPUT, index=False)

print("\n" + "=" * 40)
print("GRAPH EDGES CREATED")
print("=" * 40)

print("Total edges:", len(edges))
print("Unique DrugID 1:", edges["DrugID_1"].nunique())
print("Unique DrugID 2:", edges["DrugID_2"].nunique())

print("\nSaved:")
print(OUTPUT)

print("\nPreview:")
print(edges.head(10))