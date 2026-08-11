import pandas as pd

MASTER = "datasets/processed/master_drug_list.csv"
DGIDB = "datasets/raw/DGIdb/interactions.tsv"
OUTPUT = "datasets/processed/drug_targets.csv"


def norm(x):
    return str(x).lower().strip()


# Load master drugs
master = pd.read_csv(MASTER)

# Load DGIdb interactions
dgidb = pd.read_csv(DGIDB, sep="\t", skiprows=2)

# Normalize names
master["drug_norm"] = master["DrugName"].map(norm)
dgidb["drug_norm"] = dgidb["drug_name"].map(norm)
dgidb["drug_claim_norm"] = dgidb["drug_claim_name"].map(norm)

# Match using drug_name OR drug_claim_name
matched = dgidb[
    dgidb["drug_norm"].isin(set(master["drug_norm"])) |
    dgidb["drug_claim_norm"].isin(set(master["drug_norm"]))
].copy()

# Map DGIdb drug to our DrugID
name_to_id = dict(zip(master["drug_norm"], master["DrugID"]))

matched["DrugID"] = matched["drug_norm"].map(name_to_id)

# If drug_name didn't match, try drug_claim_name
mask = matched["DrugID"].isna()
matched.loc[mask, "DrugID"] = matched.loc[mask, "drug_claim_norm"].map(name_to_id)

# Get DrugName from master
id_to_name = dict(zip(master["DrugID"], master["DrugName"]))
matched["DrugName"] = matched["DrugID"].map(id_to_name)

# Select required features
output = matched[
    [
        "DrugID",
        "DrugName",
        "gene_name",
        "gene_concept_id",
        "interaction_types",
        "interaction_source_db_name",
        "interaction_score",
        "evidence_score"
    ]
].drop_duplicates()

# Remove invalid rows
output = output.dropna(subset=["DrugID", "gene_name"])

# Save
output.to_csv(OUTPUT, index=False)

print("=" * 60)
print("DRUG TARGET DATASET CREATED")
print("=" * 60)
print("Rows:", len(output))
print("Unique drugs:", output["DrugID"].nunique())
print("Unique targets:", output["gene_name"].nunique())
print("Saved:", OUTPUT)
print("=" * 60)