import os
import time
import requests
import pandas as pd
from tqdm import tqdm

# ---------------------------------------
# Files
# ---------------------------------------

INPUT_FILE = "datasets/processed/pubchem_data.csv"

SUCCESS_FILE = "datasets/processed/pubchem_data_result.csv"

FAILED_FILE = "datasets/processed/failed_drugs.csv"

LOG_FILE = "datasets/processed/pubchem_log.txt"

# ---------------------------------------
# Load Dataset
# ---------------------------------------

df = pd.read_csv(INPUT_FILE)

# Resume Support
if os.path.exists(SUCCESS_FILE):
    success_df = pd.read_csv(SUCCESS_FILE)
    completed = set(success_df["DrugName"].str.lower())
else:
    success_df = pd.DataFrame(columns=[
        "DrugName",
        "CID",
        "ConnectivitySMILES",
        "MolecularWeight",
        "XLogP",
        "TPSA",
        "HBondDonorCount",
        "HBondAcceptorCount",
        "RotatableBondCount"
    ])
    completed = set()

failed = []

# ---------------------------------------
# Extraction
# ---------------------------------------

for drug in tqdm(df["DrugName"]):

    if drug.lower() in completed:
        continue

    try:

        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
            f"{drug}/property/"
            "ConnectivitySMILES,"
            "MolecularWeight,"
            "XLogP,"
            "TPSA,"
            "HBondDonorCount,"
            "HBondAcceptorCount,"
            "RotatableBondCount"
            "/JSON"
        )

        response = requests.get(url, timeout=20)

        if response.status_code == 200:

            data = response.json()["PropertyTable"]["Properties"][0]

            row = {
                "DrugName": drug,
                "CID": data.get("CID"),
                "ConnectivitySMILES": data.get("ConnectivitySMILES"),
                "MolecularWeight": data.get("MolecularWeight"),
                "XLogP": data.get("XLogP"),
                "TPSA": data.get("TPSA"),
                "HBondDonorCount": data.get("HBondDonorCount"),
                "HBondAcceptorCount": data.get("HBondAcceptorCount"),
                "RotatableBondCount": data.get("RotatableBondCount")
            }

            success_df.loc[len(success_df)] = row

            success_df.to_csv(
                SUCCESS_FILE,
                index=False
            )

        else:

            failed.append({
                "DrugName": drug,
                "Reason": response.status_code
            })

    except Exception as e:

        failed.append({
            "DrugName": drug,
            "Reason": str(e)
        })

    time.sleep(0.2)

# ---------------------------------------
# Save Failed
# ---------------------------------------

pd.DataFrame(failed).to_csv(
    FAILED_FILE,
    index=False
)

# ---------------------------------------
# Log
# ---------------------------------------

with open(LOG_FILE, "w") as f:

    f.write("PubChem Extraction Completed\n")
    f.write(f"Total Drugs : {len(df)}\n")
    f.write(f"Successful : {len(success_df)}\n")
    f.write(f"Failed : {len(failed)}\n")

print("\n===================================")
print("PubChem Extraction Completed ✅")
print("===================================")
print("Total Drugs :", len(df))
print("Successful :", len(success_df))
print("Failed :", len(failed))