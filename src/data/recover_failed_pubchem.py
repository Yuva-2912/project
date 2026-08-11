import os
import time
import requests
import pandas as pd
from urllib.parse import quote

# ============================================================
# FILES
# ============================================================

FAILED_FILE = "datasets/processed/failed_drugs.csv"

RECOVERED_FILE = "datasets/processed/pubchem_recovered.csv"

UNRESOLVED_FILE = "datasets/processed/unresolved_drugs.csv"

# ============================================================
# PUBCHEM
# ============================================================

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

PROPERTY_LIST = (
    "ConnectivitySMILES,"
    "MolecularWeight,"
    "XLogP,"
    "TPSA,"
    "HBondDonorCount,"
    "HBondAcceptorCount,"
    "RotatableBondCount"
)

# ============================================================
# RESULT COLUMNS
# ============================================================

RESULT_COLUMNS = [
    "OriginalDrugName",
    "MatchedName",
    "CID",
    "ConnectivitySMILES",
    "MolecularWeight",
    "XLogP",
    "TPSA",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "RotatableBondCount",
    "Status"
]

# ============================================================
# LOAD FAILED DRUGS
# ============================================================

failed_df = pd.read_csv(FAILED_FILE)

failed_df["DrugName"] = (
    failed_df["DrugName"]
    .astype(str)
    .str.strip()
)

print("=" * 70)
print("PubChem Failed Drug Recovery")
print("=" * 70)

print("Failed Drugs :", len(failed_df))

# ============================================================
# LOAD PREVIOUS RECOVERY
# ============================================================

if os.path.exists(RECOVERED_FILE):
    recovered_df = pd.read_csv(RECOVERED_FILE)

    completed = set(
        recovered_df["OriginalDrugName"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

else:
    recovered_df = pd.DataFrame(
        columns=RESULT_COLUMNS
    )

    completed = set()

# ============================================================
# FUNCTIONS
# ============================================================

def get_properties(name):

    encoded_name = quote(name, safe="")

    url = (
        f"{BASE_URL}/compound/name/"
        f"{encoded_name}/property/"
        f"{PROPERTY_LIST}/JSON"
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


def get_synonyms(name):

    encoded_name = quote(name, safe="")

    url = (
        f"{BASE_URL}/compound/name/"
        f"{encoded_name}/synonyms/JSON"
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

            if information:

                synonyms = information[0].get(
                    "Synonym",
                    []
                )

                return synonyms

    except Exception:
        pass

    return []


def create_result(
    original_name,
    matched_name,
    data
):

    return {
        "OriginalDrugName": original_name,
        "MatchedName": matched_name,
        "CID": data.get("CID"),
        "ConnectivitySMILES": data.get(
            "ConnectivitySMILES"
        ),
        "MolecularWeight": data.get(
            "MolecularWeight"
        ),
        "XLogP": data.get(
            "XLogP"
        ),
        "TPSA": data.get(
            "TPSA"
        ),
        "HBondDonorCount": data.get(
            "HBondDonorCount"
        ),
        "HBondAcceptorCount": data.get(
            "HBondAcceptorCount"
        ),
        "RotatableBondCount": data.get(
            "RotatableBondCount"
        ),
        "Status": "Recovered"
    }


# ============================================================
# RECOVERY
# ============================================================

unresolved = []

for index, row in failed_df.iterrows():

    original_name = row["DrugName"]

    if original_name.lower() in completed:
        continue

    print("\n" + "-" * 65)
    print(
        f"[{index + 1}/{len(failed_df)}] "
        f"{original_name}"
    )

    found = False

    # --------------------------------------------------------
    # STEP 1: RETRY ORIGINAL NAME
    # --------------------------------------------------------

    for attempt in range(3):

        data = get_properties(
            original_name
        )

        if data is not None:

            result = create_result(
                original_name,
                original_name,
                data
            )

            recovered_df.loc[
                len(recovered_df)
            ] = result

            recovered_df.to_csv(
                RECOVERED_FILE,
                index=False
            )

            print(
                "✓ Recovered using original name"
            )

            found = True
            break

        time.sleep(1)

    if found:
        continue

    # --------------------------------------------------------
    # STEP 2: GET SYNONYMS
    # --------------------------------------------------------

    print("Searching PubChem synonyms...")

    synonyms = get_synonyms(
        original_name
    )

    print(
        "Synonyms found :",
        len(synonyms)
    )

    # Remove duplicates
    unique_synonyms = []

    seen = set()

    for synonym in synonyms:

        synonym = str(synonym).strip()

        key = synonym.lower()

        if key not in seen:

            seen.add(key)
            unique_synonyms.append(synonym)

    # --------------------------------------------------------
    # STEP 3: TRY SYNONYMS
    # --------------------------------------------------------

    for synonym in unique_synonyms[:30]:

        # Don't repeat original name
        if synonym.lower() == original_name.lower():
            continue

        data = get_properties(
            synonym
        )

        if data is not None:

            result = create_result(
                original_name,
                synonym,
                data
            )

            recovered_df.loc[
                len(recovered_df)
            ] = result

            recovered_df.to_csv(
                RECOVERED_FILE,
                index=False
            )

            print(
                "✓ Recovered using synonym:"
            )

            print(
                "  Original :",
                original_name
            )

            print(
                "  Matched  :",
                synonym
            )

            print(
                "  CID      :",
                data.get("CID")
            )

            found = True
            break

        time.sleep(0.2)

    # --------------------------------------------------------
    # STEP 4: UNRESOLVED
    # --------------------------------------------------------

    if not found:

        print(
            "❌ Could not recover"
        )

        unresolved.append({
            "DrugName": original_name,
            "OriginalReason": row["Reason"],
            "Status": "Unresolved"
        })

    time.sleep(0.5)

# ============================================================
# SAVE UNRESOLVED
# ============================================================

unresolved_df = pd.DataFrame(
    unresolved
)

unresolved_df.to_csv(
    UNRESOLVED_FILE,
    index=False
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("PubChem Recovery Completed")
print("=" * 70)

print(
    "Original Failed Drugs :",
    len(failed_df)
)

print(
    "Recovered Drugs       :",
    len(recovered_df)
)

print(
    "Still Unresolved      :",
    len(unresolved_df)
)

print("\nFiles Created:")

print(
    "✓",
    RECOVERED_FILE
)

print(
    "✓",
    UNRESOLVED_FILE
)

print("=" * 70)