import pandas as pd

print("=" * 60)
print("Creating Master Drug List")
print("=" * 60)

# ----------------------------
# Load RxPairEvid Dataset
# ----------------------------

rx = pd.read_csv(
    "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"
)

# ----------------------------
# Extract Drug Names
# ----------------------------

drug_a = rx["a_name"]
drug_b = rx["b_name"]

# ----------------------------
# Combine Both Columns
# ----------------------------

all_drugs = pd.concat(
    [drug_a, drug_b],
    ignore_index=True
)

# ----------------------------
# Remove Duplicates
# ----------------------------

unique_drugs = (
    all_drugs
    .dropna()
    .str.strip()
    .drop_duplicates()
    .sort_values()
    .reset_index(drop=True)
)

# ----------------------------
# Create Drug IDs
# ----------------------------

master = pd.DataFrame({
    "DrugID": range(len(unique_drugs)),
    "DrugName": unique_drugs
})

# ----------------------------
# Save
# ----------------------------

master.to_csv(
    "datasets/processed/master_drug_list.csv",
    index=False
)

# ----------------------------
# Output
# ----------------------------

print("\nMaster Drug List Created Successfully ✅")

print("\nTotal Unique Drugs :", len(master))

print("\nFirst 10 Drugs")

print(master.head(10))