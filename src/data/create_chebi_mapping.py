import pandas as pd
import requests
import time
from tqdm import tqdm

# ==========================================
# Paths
# ==========================================

input_file = "datasets/final/master_drug_table.csv"

output_file = "datasets/processed/drug_chebi_mapping.csv"

# ==========================================
# Load drug table
# ==========================================

df = pd.read_csv(input_file)

# Only drugs with valid CID
drug_df = df[df["CID"].notna()].copy()

print("Total drugs:", len(df))
print("Drugs with CID:", len(drug_df))

# ==========================================
# PubChem ChEBI lookup
# ==========================================

results = []

for _, row in tqdm(
    drug_df.iterrows(),
    total=len(drug_df)
):

    drug_name = row["DrugName"]
    cid = int(row["CID"])

    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        f"compound/cid/{cid}/identifiers/JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            identifiers = (
                data["InformationList"]
                ["Information"][0]
                .get("Identifiers", [])
            )

            chebi_id = None

            for item in identifiers:

                if item.get("Type") == "ChEBI ID":

                    chebi_id = item.get("Identifier")
                    break

            results.append({
                "DrugID": row["DrugID"],
                "DrugName": drug_name,
                "CID": cid,
                "ChEBI_ID": chebi_id
            })

        else:

            results.append({
                "DrugID": row["DrugID"],
                "DrugName": drug_name,
                "CID": cid,
                "ChEBI_ID": None
            })

    except Exception:

        results.append({
            "DrugID": row["DrugID"],
            "DrugName": drug_name,
            "CID": cid,
            "ChEBI_ID": None
        })

    time.sleep(0.2)


# ==========================================
# Create DataFrame
# ==========================================

result_df = pd.DataFrame(results)

# ==========================================
# Save
# ==========================================

result_df.to_csv(
    output_file,
    index=False
)

# ==========================================
# Summary
# ==========================================

print("\n==============================")
print("ChEBI Mapping Completed ✅")
print("==============================")

print("Total CID drugs:", len(result_df))

print(
    "ChEBI found:",
    result_df["ChEBI_ID"].notna().sum()
)

print(
    "ChEBI missing:",
    result_df["ChEBI_ID"].isna().sum()
)

print("\nSaved:")
print(output_file)