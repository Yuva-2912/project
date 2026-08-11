import os
import time
import requests
import pandas as pd
from urllib.parse import quote

# ============================================================
# FILES
# ============================================================

UNRESOLVED_FILE = "datasets/processed/unresolved_drugs.csv"

CANDIDATE_FILE = (
    "datasets/processed/pubchem_recovery_candidates.csv"
)

# ============================================================
# PUBCHEM API
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
# LOAD UNRESOLVED DRUGS
# ============================================================

df = pd.read_csv(UNRESOLVED_FILE)

df["DrugName"] = (
    df["DrugName"]
    .astype(str)
    .str.strip()
)

print("=" * 70)
print("Advanced PubChem Recovery")
print("=" * 70)

print("Unresolved Drugs :", len(df))


# ============================================================
# PUBCHEM AUTOCOMPLETE
# ============================================================

def autocomplete(name):

    encoded = quote(name, safe="")

    url = (
        f"{BASE_URL}/autocomplete/compound/"
        f"{encoded}/json"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        if response.status_code == 200:

            data = response.json()

            return data.get(
                "dictionary_terms",
                []
            )

    except Exception as e:

        print(
            "Autocomplete error:",
            e
        )

    return []


# ============================================================
# GET PROPERTIES
# ============================================================

def get_properties(name):

    encoded = quote(name, safe="")

    url = (
        f"{BASE_URL}/compound/name/"
        f"{encoded}/property/"
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


# ============================================================
# SEARCH
# ============================================================

results = []

for i, row in df.iterrows():

    original_name = row["DrugName"]

    print("\n" + "-" * 70)
    print(
        f"[{i + 1}/{len(df)}] {original_name}"
    )

    candidates = autocomplete(
        original_name
    )

    print(
        "Autocomplete candidates:",
        len(candidates)
    )

    # Remove duplicates
    unique_candidates = []

    seen = set()

    for candidate in candidates:

        candidate = str(candidate).strip()

        key = candidate.lower()

        if key not in seen:

            seen.add(key)
            unique_candidates.append(
                candidate
            )

    # Limit candidates
    unique_candidates = unique_candidates[:20]

    if not unique_candidates:

        results.append({
            "OriginalDrugName": original_name,
            "CandidateName": "",
            "CID": "",
            "ConnectivitySMILES": "",
            "MolecularWeight": "",
            "XLogP": "",
            "TPSA": "",
            "HBondDonorCount": "",
            "HBondAcceptorCount": "",
            "RotatableBondCount": "",
            "CandidateStatus": "No candidate found"
        })

        continue

    found_candidate = False

    for candidate in unique_candidates:

        print(
            "Trying:",
            candidate
        )

        properties = get_properties(
            candidate
        )

        if properties is None:
            continue

        results.append({

            "OriginalDrugName":
                original_name,

            "CandidateName":
                candidate,

            "CID":
                properties.get("CID"),

            "ConnectivitySMILES":
                properties.get(
                    "ConnectivitySMILES"
                ),

            "MolecularWeight":
                properties.get(
                    "MolecularWeight"
                ),

            "XLogP":
                properties.get(
                    "XLogP"
                ),

            "TPSA":
                properties.get(
                    "TPSA"
                ),

            "HBondDonorCount":
                properties.get(
                    "HBondDonorCount"
                ),

            "HBondAcceptorCount":
                properties.get(
                    "HBondAcceptorCount"
                ),

            "RotatableBondCount":
                properties.get(
                    "RotatableBondCount"
                ),

            "CandidateStatus":
                "Candidate found"
        })

        found_candidate = True

        # Keep first valid candidate only
        break

    if not found_candidate:

        results.append({

            "OriginalDrugName":
                original_name,

            "CandidateName":
                "",

            "CID":
                "",

            "ConnectivitySMILES":
                "",

            "MolecularWeight":
                "",

            "XLogP":
                "",

            "TPSA":
                "",

            "HBondDonorCount":
                "",

            "HBondAcceptorCount":
                "",

            "RotatableBondCount":
                "",

            "CandidateStatus":
                "Candidates found but no properties"
        })

    time.sleep(0.5)


# ============================================================
# SAVE
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    CANDIDATE_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("Advanced PubChem Recovery Completed")
print("=" * 70)

print(
    "Total unresolved :",
    len(df)
)

print(
    "Candidates found :",
    len(
        result_df[
            result_df["CandidateName"].notna()
            &
            (
                result_df["CandidateName"]
                .astype(str)
                .str.strip()
                != ""
            )
        ]
    )
)

print(
    "No candidates :",
    len(
        result_df[
            result_df["CandidateName"]
            .astype(str)
            .str.strip()
            == ""
        ]
    )
)

print("\nFile Created:")
print("✓", CANDIDATE_FILE)

print("\nIMPORTANT:")
print(
    "Candidates are NOT automatically accepted."
)
print(
    "Verify the mapping before adding them "
    "to the final PubChem dataset."
)