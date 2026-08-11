import pandas as pd

# ============================================================
# FINAL DDI TRAINING DATASET - COMPLETE SUMMARY
# ============================================================

file_path = r"D:\DDL\datasets\final\ddi_training_dataset.csv"

df = pd.read_csv(file_path)

print("=" * 70)
print("FINAL DDI TRAINING DATASET")
print("=" * 70)

# ------------------------------------------------------------
# 1. Dataset shape
# ------------------------------------------------------------
print("\nDATASET SHAPE")
print("-" * 70)
print("Total Rows    :", df.shape[0])
print("Total Columns :", df.shape[1])

# ------------------------------------------------------------
# 2. Column information
# ------------------------------------------------------------
print("\nCOLUMN INFORMATION")
print("-" * 70)

print("First 20 columns:")
print(df.columns[:20].tolist())

print("\nLast 20 columns:")
print(df.columns[-20:].tolist())

# ------------------------------------------------------------
# 3. Identify feature columns
# ------------------------------------------------------------
a_features = [col for col in df.columns if col.startswith("A_")]
b_features = [col for col in df.columns if col.startswith("B_")]

print("\nFEATURE COUNT")
print("-" * 70)
print("Drug A features :", len(a_features))
print("Drug B features :", len(b_features))
print("Total pair features :", len(a_features) + len(b_features))

# ------------------------------------------------------------
# 4. Identifier / label columns
# ------------------------------------------------------------
print("\nOTHER COLUMNS")
print("-" * 70)

other_columns = [
    col for col in df.columns
    if col not in a_features + b_features
]

print("Non-feature columns:")
for col in other_columns:
    print("  ", col)

# ------------------------------------------------------------
# 5. Label distribution
# ------------------------------------------------------------
print("\nLABEL DISTRIBUTION")
print("-" * 70)

print(df["label"].value_counts())

print("\nPercentage:")
print(df["label"].value_counts(normalize=True) * 100)

# ------------------------------------------------------------
# 6. Positive / Negative samples
# ------------------------------------------------------------
positive = (df["label"] == 1).sum()
negative = (df["label"] == 0).sum()

print("\nCLASS BALANCING")
print("-" * 70)
print("Positive samples :", positive)
print("Negative samples :", negative)

if negative != 0:
    print("Positive : Negative =",
          positive, ":", negative)

# ------------------------------------------------------------
# 7. Missing values
# ------------------------------------------------------------
print("\nMISSING VALUES")
print("-" * 70)

total_missing = df.isnull().sum().sum()

print("Total missing values :", total_missing)

if total_missing > 0:
    print("\nColumns containing missing values:")
    print(df.isnull().sum()[df.isnull().sum() > 0])

# ------------------------------------------------------------
# 8. Duplicate rows
# ------------------------------------------------------------
print("\nDUPLICATE CHECK")
print("-" * 70)

duplicate_count = df.duplicated().sum()

print("Duplicate rows :", duplicate_count)

# ------------------------------------------------------------
# 9. Data types
# ------------------------------------------------------------
print("\nDATA TYPES")
print("-" * 70)

print(df.dtypes.value_counts())

# ------------------------------------------------------------
# 10. Drug pair examples
# ------------------------------------------------------------
print("\nFIRST 5 DRUG PAIRS")
print("-" * 70)

display_columns = [
    col for col in [
        "drug_a_ik14",
        "drug_b_ik14",
        "A_DrugName",
        "B_DrugName",
        "label"
    ]
    if col in df.columns
]

print(df[display_columns].head(5).to_string(index=False))

# ------------------------------------------------------------
# 11. Sample feature values
# ------------------------------------------------------------
print("\nSAMPLE FEATURE VALUES")
print("-" * 70)

sample_feature_columns = (
    a_features[:5] +
    b_features[:5]
)

print(df[sample_feature_columns].head(3).to_string(index=False))

# ------------------------------------------------------------
# 12. Final summary
# ------------------------------------------------------------
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print("Total training samples :", len(df))
print("Total columns          :", len(df.columns))
print("Drug A features        :", len(a_features))
print("Drug B features        :", len(b_features))
print("Total ML features      :", len(a_features) + len(b_features))
print("Positive samples       :", positive)
print("Negative samples       :", negative)
print("Missing values         :", total_missing)
print("Duplicate rows         :", duplicate_count)

print("=" * 70)
print("DATASET READY FOR MODEL TRAINING")
print("=" * 70)