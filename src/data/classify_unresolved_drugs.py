import time
import requests
import pandas as pd
from urllib.parse import quote

# ============================================================
# FILES
# ============================================================

INPUT_FILE = "datasets/processed/unresolved_drugs.csv"

OUTPUT_FILE = (
    "datasets/processed/unresolved_drug_classification.csv"
)

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# ============================================================
# LOAD
# ============================================================

df = pd.read_csv(INPUT_FILE)

df["DrugName"] = (
    df["DrugName"]
    .astype(str)
    .str.strip()
)

print("=" * 70)
print("Unresolved Drug Classification")
print("=" * 70)

print("Total Drugs :", len(df))


# ============================================================
# CHECK COMPOUND RECORD
# ============================================================

def check_compound(name):

    encoded = quote(name, safe="")

    url = (
        f"{BASE_URL}/compound/name/"
        f"{encoded}/property/"
        "CID,ConnectivitySMILES,MolecularWeight/"
        "JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code == 200:

            data = response.json()

            properties = (
                data
                .get("PropertyTable", {})
                .get("Properties", [])
            )

            if properties:

                return properties[0]

    except Exception:
        pass

    return None


# ============================================================
# CHECK SUBSTANCE RECORD
# ============================================================

def check_substance(name):

    encoded = quote(name, safe="")

    url = (
        f"{BASE_URL}/substance/name/"
        f"{encoded}/sids/JSON"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code == 200:

            data = response.json()

            information = (
                data
                .get("InformationList", {})
                .get("Information", [])
            )

            sids = []

            for item in information:

                for sid in item.get(
                    "SID",
                    []
                ):

                    sids.append(sid)

            return sids

    except Exception:
        pass

    return []


# ============================================================
# CLASSIFICATION
# ============================================================

results = []

for index, row in df.iterrows():

    name = row["DrugName"]

    print("\n" + "-" * 70)
    print(
        f"[{index + 1}/{len(df)}] {name}"
    )

    # --------------------------------------------------------
    # 1. Compound check
    # --------------------------------------------------------

    compound = check_compound(name)

    if compound:

        print("✓ Compound record found")

        results.append({
            "DrugName": name,
            "RepresentationType": "Compound",
            "CID": compound.get("CID"),
            "ConnectivitySMILES": compound.get(
                "ConnectivitySMILES"
            ),
            "MolecularWeight": compound.get(
                "MolecularWeight"
            ),
            "SubstanceRecordAvailable": True,
            "Status": "Structurally usable"
        })

        continue

    # --------------------------------------------------------
    # 2. Substance check
    # --------------------------------------------------------

    print("Compound not found")
    print("Checking substance records...")

    sids = check_substance(name)

    if len(sids) > 0:

        print(
            "✓ Substance record found"
        )

        results.append({
            "DrugName": name,
            "RepresentationType": "Substance",
            "CID": "",
            "ConnectivitySMILES": "",
            "MolecularWeight": "",
            "SubstanceRecordAvailable": True,
            "Status": "Needs component/structure review"
        })

    else:

        print(
            "❌ No compound/substance record found"
        )

        results.append({
            "DrugName": name,
            "RepresentationType": "Unknown",
            "CID": "",
            "ConnectivitySMILES": "",
            "MolecularWeight": "",
            "SubstanceRecordAvailable": False,
            "Status": "No PubChem record found"
        })

    time.sleep(0.5)


# ============================================================
# SAVE
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("Classification Completed ✅")
print("=" * 70)

print(
    "\nCompound:",
    (
        result_df["RepresentationType"]
        == "Compound"
    ).sum()
)

print(
    "Substance:",
    (
        result_df["RepresentationType"]
        == "Substance"
    ).sum()
)

print(
    "Unknown:",
    (
        result_df["RepresentationType"]
        == "Unknown"
    ).sum()
)

print("\nOutput:")
print("✓", OUTPUT_FILE)

print("\nClassification:")
print(
    result_df[
        [
            "DrugName",
            "RepresentationType",
            "Status"
        ]
    ].to_string(index=False)
)