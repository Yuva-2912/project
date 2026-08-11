import pandas as pd

UNIFIED_FILE = "datasets/final/unified_drug_features.csv"
DDI_FILE = "datasets/raw/RxPairEvid/ddi_pairs_50k.csv"

print("=" * 70)
print("CHECKING DRUG NAME AND INCHIKEY MAPPING")
print("=" * 70)

unified = pd.read_csv(UNIFIED_FILE)
ddi = pd.read_csv(DDI_FILE)

# ============================================================
# SHOW DRUG NAME SAMPLES
# ============================================================

print("\nUNIFIED DRUG NAMES")
print("-" * 70)

print(unified[["DrugID", "DrugName"]].head(20).to_string(index=False))

print("\nDDI DRUG NAMES")
print("-" * 70)

print(
    ddi[
        ["drug_a_ik14", "a_name", "drug_b_ik14", "b_name"]
    ].head(20).to_string(index=False)
)


# ============================================================
# NAME OVERLAP
# ============================================================

unified_names = set(
    unified["DrugName"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
)

a_names = set(
    ddi["a_name"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
)

b_names = set(
    ddi["b_name"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
)

print("\n" + "=" * 70)
print("NAME MATCHING")
print("=" * 70)

a_overlap = unified_names & a_names
b_overlap = unified_names & b_names

print(f"Unique unified drug names : {len(unified_names)}")
print(f"Unique DDI Drug A names   : {len(a_names)}")
print(f"Unique DDI Drug B names   : {len(b_names)}")

print(f"\nDrug A name matches: {len(a_overlap)}")
print(f"Drug B name matches: {len(b_overlap)}")


# ============================================================
# DISPLAY MATCHES
# ============================================================

print("\nSample Drug A matches:")
print(list(a_overlap)[:30])

print("\nSample Drug B matches:")
print(list(b_overlap)[:30])


# ============================================================
# CHECK POSSIBLE INCHIKEY COLUMNS
# ============================================================

print("\n" + "=" * 70)
print("SEARCHING UNIFIED DATA FOR INCHIKEY-LIKE VALUES")
print("=" * 70)

sample_a = str(ddi["drug_a_ik14"].dropna().iloc[0])
sample_b = str(ddi["drug_b_ik14"].dropna().iloc[0])

print(f"Example Drug A InChIKey14: {sample_a}")
print(f"Example Drug B InChIKey14: {sample_b}")

for col in unified.columns:

    if unified[col].dtype == "object":

        values = set(
            unified[col]
            .dropna()
            .astype(str)
            .str.strip()
        )

        a_found = sample_a in values
        b_found = sample_b in values

        if a_found or b_found:
            print(
                f"\nFOUND in column: {col}"
            )

            print(
                "Drug A found:",
                a_found
            )

            print(
                "Drug B found:",
                b_found
            )


# ============================================================
# CHECK SOURCE FILES
# ============================================================

print("\n" + "=" * 70)
print("CHECKING RAW/PROCESSED FILES")
print("=" * 70)

import os

for root, dirs, files in os.walk("datasets"):

    for file in files:

        if file.lower().endswith(
            (".csv", ".tsv", ".txt", ".parquet")
        ):

            path = os.path.join(root, file)

            print(path)

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)