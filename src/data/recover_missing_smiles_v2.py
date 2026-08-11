import pandas as pd
import requests
import time
from pathlib import Path

print("=" * 60)
print("MISSING SMILES RECOVERY - PUBCHEM V2")
print("=" * 60)

MISSING_PATH = Path(
    "datasets/processed/missing_smiles_drugs.csv"
)

OUTPUT_PATH = Path(
    "datasets/processed/recovered_smiles_v2.csv"
)

missing = pd.read_csv(MISSING_PATH)

print("\nMissing drugs:", len(missing))


# ============================================================
# STEP 1: FIND CID
# ============================================================

def find_cid(drug_name):

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        "compound/name/"
        + requests.utils.quote(str(drug_name))
        + "/cids/JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        cids = data.get("IdentifierList", {}).get("CID", [])

        if not cids:
            return None

        return cids[0]

    except Exception:
        return None


# ============================================================
# STEP 2: GET SMILES FROM CID
# ============================================================

def get_smiles(cid):

    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
        "compound/cid/"
        f"{cid}/property/"
        "ConnectivitySMILES/JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        properties = (
            data
            .get("PropertyTable", {})
            .get("Properties", [])
        )

        if not properties:
            return None

        return properties[0].get("ConnectivitySMILES")

    except Exception:
        return None


# ============================================================
# RECOVERY
# ============================================================

results = []

for i, row in missing.iterrows():

    drug_id = row["DrugID"]
    drug_name = row["DrugName"]

    print(
        f"[{i + 1}/{len(missing)}] {drug_name}"
    )

    # --------------------------------------------------------
    # Find CID
    # --------------------------------------------------------

    cid = find_cid(drug_name)

    if cid is None:

        print("   ❌ CID not found")

        results.append({
            "DrugID": drug_id,
            "DrugName": drug_name,
            "CID": None,
            "ConnectivitySMILES": None,
            "RecoveryStatus": "CID_Not_Found"
        })

        time.sleep(0.3)
        continue

    print(f"   CID found: {cid}")

    # --------------------------------------------------------
    # Get SMILES
    # --------------------------------------------------------

    smiles = get_smiles(cid)

    if smiles:

        print("   ✅ SMILES recovered")

        results.append({
            "DrugID": drug_id,
            "DrugName": drug_name,
            "CID": cid,
            "ConnectivitySMILES": smiles,
            "RecoveryStatus": "Recovered"
        })

    else:

        print("   ⚠️ CID found but SMILES unavailable")

        results.append({
            "DrugID": drug_id,
            "DrugName": drug_name,
            "CID": cid,
            "ConnectivitySMILES": None,
            "RecoveryStatus": "CID_Found_No_SMILES"
        })

    time.sleep(0.3)


# ============================================================
# SAVE
# ============================================================

recovered = pd.DataFrame(results)

recovered.to_csv(
    OUTPUT_PATH,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("RECOVERY SUMMARY")
print("=" * 60)

print(
    "Total attempted:",
    len(recovered)
)

print(
    "CID found:",
    recovered["CID"].notna().sum()
)

print(
    "SMILES recovered:",
    recovered["ConnectivitySMILES"].notna().sum()
)

print(
    "CID not found:",
    (
        recovered["RecoveryStatus"]
        == "CID_Not_Found"
    ).sum()
)

print(
    "CID found but no SMILES:",
    (
        recovered["RecoveryStatus"]
        == "CID_Found_No_SMILES"
    ).sum()
)

print("\nSaved:")
print(OUTPUT_PATH)

print("\nResults:")
print(
    recovered.to_string(index=False)
)