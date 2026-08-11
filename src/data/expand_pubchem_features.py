import os
import time
import requests
import pandas as pd


# ============================================================
# FILES
# ============================================================

MASTER_FILE = "datasets/final/master_drug_table.csv"

OUTPUT_FILE = "datasets/processed/chemical_features.csv"

FAILURE_FILE = "datasets/processed/pubchem_feature_failures.csv"


# ============================================================
# SETTINGS
# ============================================================

BASE_URL = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    "compound/cid/{cid}/property/{property}/JSON"
)

REQUEST_DELAY = 0.25
RETRY_COUNT = 3
CHECKPOINT_EVERY = 1


# ============================================================
# IMPORTANT PUBCHEM PROPERTIES
# ============================================================

PROPERTIES = {

    "MolecularFormula":
        "MolecularFormula",

    "MolecularWeight":
        "MolecularWeight",

    "ExactMass":
        "ExactMass",

    "MonoisotopicMass":
        "MonoisotopicMass",

    "HeavyAtomCount":
        "HeavyAtomCount",

    "Charge":
        "FormalCharge",

    "XLogP":
        "XLogP",

    "TPSA":
        "TPSA",

    "HBondDonorCount":
        "HBondDonorCount",

    "HBondAcceptorCount":
        "HBondAcceptorCount",

    "RotatableBondCount":
        "RotatableBondCount",

    "Complexity":
        "Complexity",

    "CanonicalSMILES":
        "ConnectivitySMILES",

    "IsomericSMILES":
        "IsomericSMILES",

    "InChI":
        "InChI",

    "InChIKey":
        "InChIKey"
}


# ============================================================
# CREATE OUTPUT COLUMNS
# ============================================================

OUTPUT_COLUMNS = [
    "DrugID",
    "DrugName",
    "CID"
]

OUTPUT_COLUMNS += list(
    PROPERTIES.values()
)

OUTPUT_COLUMNS += [
    "PubChemStatus"
]


# ============================================================
# ATOMIC SAVE
# ============================================================

def save_checkpoint(df):

    temp_file = OUTPUT_FILE + ".tmp"

    df.to_csv(
        temp_file,
        index=False
    )

    os.replace(
        temp_file,
        OUTPUT_FILE
    )


# ============================================================
# LOAD MASTER
# ============================================================

print("=" * 70)
print("SAFE PUBCHEM CHEMICAL FEATURE COLLECTION")
print("=" * 70)

master = pd.read_csv(
    MASTER_FILE
)

print(
    "\nMaster Drugs :",
    len(master)
)


# ============================================================
# PREPARE MASTER
# ============================================================

master["CID_numeric"] = pd.to_numeric(
    master["CID"],
    errors="coerce"
)


# ============================================================
# RESUME FROM PREVIOUS CHECKPOINT
# ============================================================
if os.path.exists(OUTPUT_FILE):

    print(
        "\nExisting checkpoint found."
    )

    result = pd.read_csv(
        OUTPUT_FILE,
        dtype=str
    )

    print(
        "Checkpoint records :",
        len(result)
    )

    # Make sure all expected columns exist
    for column in OUTPUT_COLUMNS:

        if column not in result.columns:

            result[column] = pd.NA

    result = result[
        OUTPUT_COLUMNS
    ]

    # --------------------------------------------------------
    # IMPORTANT:
    # PubChem properties can be numeric OR textual.
    # Keep all property columns as object/string.
    # This prevents Pandas dtype errors.
    # --------------------------------------------------------

    for column in PROPERTIES.values():

        result[column] = result[column].astype("object")

else:

    print(
        "\nNo previous checkpoint found."
    )

    result = master[
        ["DrugID", "DrugName", "CID"]
    ].copy()

    for column in PROPERTIES.values():

        result[column] = pd.Series(
            pd.NA,
            index=result.index,
            dtype="object"
        )

    result["PubChemStatus"] = "Pending"
# ============================================================
# CREATE FAILURE FILE
# ============================================================

if os.path.exists(FAILURE_FILE):

    failures = pd.read_csv(
        FAILURE_FILE
    )

else:

    failures = pd.DataFrame(
        columns=[
            "DrugID",
            "DrugName",
            "CID",
            "Property",
            "Status",
            "Reason"
        ]
    )


# ============================================================
# FETCH ONE PROPERTY
# ============================================================

session = requests.Session()


def fetch_property(cid, pubchem_property):

    url = BASE_URL.format(
        cid=cid,
        property=pubchem_property
    )

    for attempt in range(
        1,
        RETRY_COUNT + 1
    ):

        try:

            response = session.get(
                url,
                timeout=45
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                data = response.json()

                properties = (
                    data
                    .get("PropertyTable", {})
                    .get("Properties", [])
                )

                if len(properties) == 0:

                    return None, "No property returned"

                value = properties[0].get(
                    pubchem_property
                )

                return value, None


            # ------------------------------------------------
            # NOT FOUND
            # ------------------------------------------------

            elif response.status_code == 404:

                return None, "404 - Property not available"


            # ------------------------------------------------
            # BAD REQUEST
            # ------------------------------------------------

            elif response.status_code == 400:

                return None, "400 - Invalid PubChem request"


            # ------------------------------------------------
            # RATE LIMIT / SERVER ERROR
            # ------------------------------------------------

            elif response.status_code in [
                429,
                500,
                502,
                503,
                504
            ]:

                wait_time = 3 * attempt

                print(
                    f"\n    HTTP {response.status_code}"
                    f" - retrying in {wait_time}s"
                )

                time.sleep(
                    wait_time
                )

            else:

                return None, (
                    f"HTTP {response.status_code}"
                )

        except Exception as e:

            if attempt == RETRY_COUNT:

                return None, str(e)

            time.sleep(
                3 * attempt
            )

    return None, "Failed after retries"


# ============================================================
# PROCESS DRUGS
# ============================================================

total_drugs = len(result)

processed = 0
available = 0
unresolved = 0


for index in result.index:

    drug_id = result.at[
        index,
        "DrugID"
    ]

    drug_name = result.at[
        index,
        "DrugName"
    ]

    cid_value = result.at[
        index,
        "CID"
    ]

    # --------------------------------------------------------
    # SKIP ALREADY COMPLETED DRUGS
    # --------------------------------------------------------

    current_status = str(
        result.at[
            index,
            "PubChemStatus"
        ]
    )

    if current_status == "Available":

        continue


    # --------------------------------------------------------
    # CID CHECK
    # --------------------------------------------------------

    if pd.isna(cid_value):

        result.at[
            index,
            "PubChemStatus"
        ] = "Unresolved"

        unresolved += 1

        save_checkpoint(
            result
        )

        continue


    try:

        cid = int(
            float(cid_value)
        )

    except:

        result.at[
            index,
            "PubChemStatus"
        ] = "Unresolved"

        unresolved += 1

        save_checkpoint(
            result
        )

        continue


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print(
        "\n" + "-" * 70
    )

    print(
        f"Drug {processed + 1}/{total_drugs}"
    )

    print(
        f"DrugID : {drug_id}"
    )

    print(
        f"Drug   : {drug_name}"
    )

    print(
        f"CID    : {cid}"
    )


    drug_success_count = 0


    # --------------------------------------------------------
    # FETCH PROPERTIES
    # --------------------------------------------------------

    for pubchem_property, output_column in (
        PROPERTIES.items()
    ):

        # Skip if already collected
        existing_value = result.at[
            index,
            output_column
        ]

        if pd.notna(existing_value):

            drug_success_count += 1

            continue


        print(
            f"  → {output_column}",
            end=" ",
            flush=True
        )


        value, error = fetch_property(
            cid,
            pubchem_property
        )


        if error is None:

            result.at[
                index,
                output_column
            ] = value

            drug_success_count += 1

            print(
                "✓"
            )

        else:

            print(
                f"✗ {error}"
            )

            new_failure = pd.DataFrame([
                {
                    "DrugID": drug_id,
                    "DrugName": drug_name,
                    "CID": cid,
                    "Property": output_column,
                    "Status": "Failed",
                    "Reason": error
                }
            ])

            failures = pd.concat(
                [
                    failures,
                    new_failure
                ],
                ignore_index=True
            )

        time.sleep(
            REQUEST_DELAY
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if drug_success_count > 0:

        result.at[
            index,
            "PubChemStatus"
        ] = "Available"

        available += 1

    else:

        result.at[
            index,
            "PubChemStatus"
        ] = "Unresolved"

        unresolved += 1


    # --------------------------------------------------------
    # CHECKPOINT
    # --------------------------------------------------------

    save_checkpoint(
        result
    )

    failures.to_csv(
        FAILURE_FILE,
        index=False
    )

    processed += 1


    print(
        f"\nCheckpoint saved."
    )

    print(
        f"Properties collected: "
        f"{drug_success_count}/{len(PROPERTIES)}"
    )


# ============================================================
# FINAL SAVE
# ============================================================

save_checkpoint(
    result
)

failures.to_csv(
    FAILURE_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("PUBCHEM CHEMICAL FEATURE COLLECTION COMPLETED ✅")
print("=" * 70)

print(
    "Total Drugs :",
    len(result)
)

print(
    "Available   :",
    (
        result["PubChemStatus"]
        == "Available"
    ).sum()
)

print(
    "Unresolved   :",
    (
        result["PubChemStatus"]
        == "Unresolved"
    ).sum()
)

print(
    "Failure Records :",
    len(failures)
)


print("\nFeature Coverage")
print("-" * 70)

for column in PROPERTIES.values():

    count = result[
        column
    ].notna().sum()

    percentage = (
        count / len(result)
    ) * 100

    print(
        f"{column:25} "
        f"{count:4}/{len(result)} "
        f"({percentage:.2f}%)"
    )


print("\nFiles Created / Updated:")
print(
    "✓",
    OUTPUT_FILE
)

print(
    "✓",
    FAILURE_FILE
)

print("\nAll 3170 drugs are retained.")