import pandas as pd
import os

INPUT = "datasets/final/master_drug_table.csv"
OUTPUT = "datasets/processed/drug_smiles.csv"

print("=" * 40)
print("CREATING DRUG SMILES DATASET")
print("=" * 40)

df = pd.read_csv(INPUT)

print("Input shape:", df.shape)

smiles_df = df[[
    "DrugID",
    "DrugName",
    "ConnectivitySMILES"
]].copy()

smiles_df = smiles_df.dropna(subset=["ConnectivitySMILES"])

smiles_df.to_csv(OUTPUT, index=False)

print("\nSMILES DATASET CREATED")
print("Rows:", len(smiles_df))
print("Columns:", smiles_df.columns.tolist())
print("Saved:", OUTPUT)

print("\nPreview:")
print(smiles_df.head())