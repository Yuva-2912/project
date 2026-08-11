import pandas as pd

# ============================================================
# FILES
# ============================================================

MASTER_FILE = "datasets/processed/master_drug_list.csv"
RXPAIR_FILE = "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"
UNRESOLVED_FILE = "datasets/processed/unresolved_drugs.csv"

OUTPUT_FILE = "datasets/processed/unresolved_ddi_check.csv"

# ============================================================
# LOAD DATA
# ============================================================

master = pd.read_csv(MASTER_FILE)
rxpair = pd.read_csv(RXPAIR_FILE)
unresolved = pd.read_csv(UNRESOLVED_FILE)

# ============================================================
# NORMALIZE NAMES
# ============================================================

def normalize_name(value):
    return (
        str(value)
        .strip()
        .lower()
    )

unresolved["DrugName_key"] = (
    unresolved["DrugName"]
    .apply(normalize_name)
)

rxpair["a_name_key"] = (
    rxpair["a_name"]
    .apply(normalize_name)
)

rxpair["b_name_key"] = (
    rxpair["b_name"]
    .apply(normalize_name)
)

# ============================================================
# CHECK EACH UNRESOLVED DRUG
# ============================================================

results = []

for _, row in unresolved.iterrows():

    drug = row["DrugName"]
    drug_key = row["DrugName_key"]

    a_matches = rxpair[
        rxpair["a_name_key"] == drug_key
    ]

    b_matches = rxpair[
        rxpair["b_name_key"] == drug_key
    ]

    total_matches = len(a_matches) + len(b_matches)

    results.append({
        "DrugName": drug,
        "Appears_as_DrugA": len(a_matches) > 0,
        "Appears_as_DrugB": len(b_matches) > 0,
        "DrugA_Count": len(a_matches),
        "DrugB_Count": len(b_matches),
        "Total_DDI_Records": total_matches,
        "Required_for_DDI_Model": total_matches > 0
    })

# ============================================================
# SAVE RESULT
# ============================================================

result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

required = result_df[
    result_df["Required_for_DDI_Model"] == True
]

not_required = result_df[
    result_df["Required_for_DDI_Model"] == False
]

print("=" * 70)
print("Unresolved Drug DDI Check Completed ✅")
print("=" * 70)

print(
    "\nTotal Unresolved Drugs :",
    len(result_df)
)

print(
    "Used in DDI Dataset    :",
    len(required)
)

print(
    "Not Used in DDI Dataset:",
    len(not_required)
)

print("\n-----------------------------------")
print("Drugs Required for DDI Model")
print("-----------------------------------")

if len(required) > 0:
    print(
        required[
            [
                "DrugName",
                "DrugA_Count",
                "DrugB_Count",
                "Total_DDI_Records"
            ]
        ].to_string(index=False)
    )
else:
    print("None")

print("\n-----------------------------------")
print("Drugs NOT Required for DDI Model")
print("-----------------------------------")

if len(not_required) > 0:
    print(
        not_required[
            [
                "DrugName",
                "Total_DDI_Records"
            ]
        ].to_string(index=False)
    )
else:
    print("None")

print("\nFile Created:")
print("✓", OUTPUT_FILE)