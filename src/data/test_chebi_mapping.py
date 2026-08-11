import requests

cid = 2244

url = (
    f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    f"compound/cid/{cid}/identifiers/JSON"
)

response = requests.get(url, timeout=10)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("\nPubChem Identifiers:\n")
    print(data)

else:
    print("Failed to retrieve identifiers.")
    print(response.text)