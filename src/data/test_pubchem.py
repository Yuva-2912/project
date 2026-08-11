import pandas as pd
import requests

master = pd.read_csv(
    "datasets/processed/master_drug_list_cleaned.csv"
)

print("=" * 70)
print("PubChem API Test")
print("=" * 70)

for _, row in master.head(10).iterrows():

    drug = row["CleanName"]

    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{drug}/property/"
        "CID,CanonicalSMILES,MolecularWeight,XLogP,TPSA/JSON"
    )

    print(f"\nDrug : {drug}")

    try:

        response = requests.get(url, timeout=20)

        if response.status_code == 200:

            data = response.json()

            prop = data["PropertyTable"]["Properties"][0]

            print("✅ Found")
            print("CID :", prop.get("CID"))
            print("SMILES :", prop.get("CanonicalSMILES"))
            print("MW :", prop.get("MolecularWeight"))
            print("XLogP :", prop.get("XLogP"))
            print("TPSA :", prop.get("TPSA"))

        else:

            print("❌ Not Found")

    except Exception as e:

        print("Error :", e)