import pandas as pd
import requests
import time
from pathlib import Path

# ============================================================
# RECOVER MISSING SMILES FROM PUBCHEM
# ============================================================

print("=" * 60)
print("RECOVERING MISSING SMILES")
print("=" * 60)

MASTER_PATH = Path("datasets/final/master_drug_table.csv")
MISSING_PATH = Path("datasets/processed/missing_smiles_drugs.csv")

OUTPUT_PATH = Path("datasets/processed/recovered_smiles.csv")

# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

master = pd.read_csv(MASTER_PATH)
missing = pd.read_csv(MISSING_PATH)

print("\nMaster drugs:", len(master))
print("Missing drugs:", len(missing))

# ------------------------------------------------------------
# PubChem lookup
# ------------------------------------------------------------

def pubchem_lookup(drug_name):

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        "compound/name/"
        + requests.utils.quote(str(drug_name))
        + "/property/"
        "CanonicalSMILES,ConnectivitySMILES,"
        "MolecularWeight,XLogP,TPSA,"
        "HBondDonorCount,HBondAcceptorCount,"
        "RotatableBondCount/JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        properties = data["PropertyTable"]["Properties"]

        if len(properties) == 0:
            return None

        return properties[0]

    except Exception:
        return None


# ------------------------------------------------------------
# Recover
# ------------------------------------------------------------

results = []

for index, row in missing.iterrows():

    drug_id = row["DrugID"]
    drug_name = row["DrugName"]

    print(
        f"[{index + 1}/{len(missing)}] "
        f"{drug_name}"
    )

    result = pubchem_lookup(drug_name)

    if result is None:

        print("   ❌ Not found")

        results.append({
            "DrugID": drug_id,
            "DrugName": drug_name,
            "CID": None,
            "ConnectivitySMILES": None,
            "MolecularWeight": None,
            "XLogP": None,
            "TPSA": None,
            "HBondDonorCount": None,
            "HBondAcceptorCount": None,
            "RotatableBondCount": None,
            "RecoveryStatus": "Not found"
        })

    else:

        smiles = result.get("ConnectivitySMILES")

        print(
            "   ✅ Found",
            f"(CID: {result.get('CID')})"
        )

        results.append({
            "DrugID": drug_id,
            "DrugName": drug_name,
            "CID": result.get("CID"),
            "ConnectivitySMILES": smiles,
            "MolecularWeight": result.get("MolecularWeight"),
            "XLogP": result.get("XLogP"),
            "TPSA": result.get("TPSA"),
            "HBondDonorCount": result.get("HBondDonorCount"),
            "HBondAcceptorCount": result.get("HBondAcceptorCount"),
            "RotatableBondCount": result.get("RotatableBondCount"),
            "RecoveryStatus": (
                "Recovered"
                if smiles
                else "Found_No_SMILES"
            )
        })

    time.sleep(0.2)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

recovered = pd.DataFrame(results)

recovered.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 60)
print("RECOVERY SUMMARY")
print("=" * 60)

print(
    "Total attempted:",
    len(recovered)
)

print(
    "Recovered with SMILES:",
    recovered["ConnectivitySMILES"].notna().sum()
)

print(
    "Still unresolved:",
    recovered["ConnectivitySMILES"].isna().sum()
)

print("\nSaved:")
print(OUTPUT_PATH)

print("\nResults:")
print(
    recovered[
        [
            "DrugID",
            "DrugName",
            "CID",
            "ConnectivitySMILES",
            "RecoveryStatus"
        ]
    ].to_string(index=False)
)