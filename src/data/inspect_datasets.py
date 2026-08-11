import pandas as pd

print("=" * 70)
print("RxPairEvid Dataset")
print("=" * 70)

rx = pd.read_csv("datasets/raw/RxPairEvid/ddi_pairs_50k.csv")

print("\nShape:")
print(rx.shape)

print("\nColumns:")
print(rx.columns.tolist())

print("\nFirst 5 Rows:")
print(rx.head())

print("\n" + "=" * 70)
print("SIDER - Drug Names")
print("=" * 70)

drug_names = pd.read_csv(
    "datasets/raw/SIDER/drug_names.tsv",
    sep="\t",
    header=None
)

print("\nShape:")
print(drug_names.shape)

print("\nFirst 5 Rows:")
print(drug_names.head())

print("\n" + "=" * 70)
print("SIDER - Side Effects")
print("=" * 70)

side_effects = pd.read_csv(
    "datasets/raw/SIDER/meddra_all_se.tsv.gz",
    sep="\t",
    compression="gzip",
    header=None
)

print("\nShape:")
print(side_effects.shape)

print("\nFirst 5 Rows:")
print(side_effects.head())