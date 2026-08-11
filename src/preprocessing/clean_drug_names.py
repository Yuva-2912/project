import pandas as pd
import re

# ----------------------------
# Load Master Drug List
# ----------------------------

master = pd.read_csv(
    "datasets/processed/master_drug_list.csv"
)

# ----------------------------
# Drug Name Cleaning Function
# ----------------------------

def clean_name(name):

    if pd.isna(name):
        return name

    # Remove anything inside brackets
    name = re.sub(r"\([^)]*\)", "", name)

    # Remove + symbols
    name = name.replace("+", "")

    # Remove extra hyphens at beginning
    name = re.sub(r"^-+", "", name)

    # Remove extra spaces
    name = " ".join(name.split())

    return name.strip()

# ----------------------------
# Apply Cleaning
# ----------------------------

master["CleanName"] = master["DrugName"].apply(clean_name)

# ----------------------------
# Save
# ----------------------------

master.to_csv(
    "datasets/processed/master_drug_list_cleaned.csv",
    index=False
)

print("=" * 60)
print("Drug Name Cleaning Completed ✅")
print("=" * 60)

print(master[["DrugName", "CleanName"]].head(20))