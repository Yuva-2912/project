import os
import re
import numpy as np
import pandas as pd

# ============================================================
# CREATE SMILES SEQUENCE FEATURES
# ============================================================

print("=" * 60)
print("CREATING SMILES SEQUENCE FEATURES")
print("=" * 60)

MASTER_PATH = "datasets/processed/master_drug_list.csv"
SMILES_PATH = "datasets/processed/drug_smiles.csv"
OUTPUT_PATH = "datasets/final/smiles_features.csv"

MAX_LENGTH = 150

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

master = pd.read_csv(MASTER_PATH)
smiles_df = pd.read_csv(SMILES_PATH)

print(f"Master shape : {master.shape}")
print(f"SMILES shape : {smiles_df.shape}")

# ------------------------------------------------------------
# CLEAN SMILES
# ------------------------------------------------------------

smiles_df["ConnectivitySMILES"] = (
    smiles_df["ConnectivitySMILES"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# ------------------------------------------------------------
# BUILD CHARACTER VOCABULARY
# ------------------------------------------------------------

special_tokens = ["<PAD>", "<UNK>", "<START>", "<END>"]

all_chars = set()

for smiles in smiles_df["ConnectivitySMILES"]:
    all_chars.update(smiles)

vocab = special_tokens + sorted(all_chars)

char_to_id = {
    char: idx
    for idx, char in enumerate(vocab)
}

print(f"Vocabulary size: {len(vocab)}")

# ------------------------------------------------------------
# ENCODE FUNCTION
# ------------------------------------------------------------

PAD_ID = char_to_id["<PAD>"]
UNK_ID = char_to_id["<UNK>"]
START_ID = char_to_id["<START>"]
END_ID = char_to_id["<END>"]


def encode_smiles(smiles):

    if not smiles:
        return [PAD_ID] * MAX_LENGTH

    tokens = [START_ID]

    for char in smiles:
        tokens.append(char_to_id.get(char, UNK_ID))

    tokens.append(END_ID)

    # Truncate
    tokens = tokens[:MAX_LENGTH]

    # Padding
    if len(tokens) < MAX_LENGTH:
        tokens.extend(
            [PAD_ID] * (MAX_LENGTH - len(tokens))
        )

    return tokens


# ------------------------------------------------------------
# CREATE SMILES MAPPING
# ------------------------------------------------------------

smiles_map = dict(
    zip(
        smiles_df["DrugID"],
        smiles_df["ConnectivitySMILES"]
    )
)

# ------------------------------------------------------------
# CREATE FEATURES FOR ALL MASTER DRUGS
# ------------------------------------------------------------

records = []

missing_count = 0

for _, row in master.iterrows():

    drug_id = row["DrugID"]
    drug_name = row["DrugName"]

    smiles = smiles_map.get(drug_id, "")

    if pd.isna(smiles):
        smiles = ""

    smiles = str(smiles).strip()

    if smiles == "":
        missing = 1
        missing_count += 1
    else:
        missing = 0

    encoded = encode_smiles(smiles)

    record = {
        "DrugID": drug_id,
        "DrugName": drug_name,
        "SMILESAvailable": 1 - missing,
        "SMILESMissing": missing,
    }

    for i, value in enumerate(encoded):
        record[f"SMILES_{i}"] = value

    records.append(record)


features = pd.DataFrame(records)

# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------

print()
print("=" * 60)
print("SMILES FEATURES CREATED")
print("=" * 60)

print(f"Rows              : {len(features)}")
print(f"Columns           : {len(features.columns)}")
print(f"Missing SMILES    : {missing_count}")
print(f"Available SMILES  : {len(features) - missing_count}")
print(f"Sequence length   : {MAX_LENGTH}")
print(f"Vocabulary size   : {len(vocab)}")

print()
print("Expected:")
print(f"Master drugs      : {len(master)}")
print(f"Feature rows      : {len(features)}")

# ------------------------------------------------------------
# CHECK DRUG ID ALIGNMENT
# ------------------------------------------------------------

master_ids = set(master["DrugID"])
feature_ids = set(features["DrugID"])

missing_ids = master_ids - feature_ids
extra_ids = feature_ids - master_ids

print()
print("DRUG ID ALIGNMENT")
print(f"Missing IDs : {len(missing_ids)}")
print(f"Extra IDs   : {len(extra_ids)}")

if missing_ids:
    print("Missing DrugIDs:", sorted(missing_ids))

if extra_ids:
    print("Extra DrugIDs:", sorted(extra_ids))

# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)

features.to_csv(
    OUTPUT_PATH,
    index=False
)

print()
print("Saved:")
print(OUTPUT_PATH)

print()
print("Preview:")
print(features.head())

print()
print("=" * 60)
print("DONE")
print("=" * 60)