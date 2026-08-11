import pandas as pd
import glob
import os

DRUGS = [
    "Sucralfate",
    "Iron polymaltose",
    "Iron sucrose",
    "Hydrolyzed Cephalothin",
    "Colistimethate",
    "Nitroprusside",
    "Pentosan polysulfate",
    "Gleptoferron",
    "Polythiazide",
    "Benzylpenicilloyl polylysine",
    "Ivermectin",
    "Kitasamycin",
    "Radium Ra-223 cation",
    "Sevelamer",
    "Octylphenoxy polyethoxyethanol",
    "Kaolin",
    "1,6-Fructose Diphosphate (Linear Form)",
    "Dihematoporphyrin ether",
    "Cephalosporin analog"
]

print("=" * 70)
print("SEARCHING ALL LOCAL DATA SOURCES")
print("=" * 70)

files = glob.glob("datasets/**/*", recursive=True)

for file in files:

    if not os.path.isfile(file):
        continue

    ext = os.path.splitext(file)[1].lower()

    if ext not in [".csv", ".tsv", ".gz"]:
        continue

    print("\nFILE:", file)

    try:

        if file.endswith(".csv"):
            df = pd.read_csv(file, low_memory=False)

        elif file.endswith(".tsv"):
            df = pd.read_csv(
                file,
                sep="\t",
                low_memory=False
            )

        elif file.endswith(".gz"):
            df = pd.read_csv(
                file,
                sep="\t",
                compression="gzip",
                low_memory=False
            )

        else:
            continue

        # Search only object/string columns
        text_columns = df.select_dtypes(
            include=["object", "string"]
        ).columns

        found = set()

        for column in text_columns:

            series = df[column].fillna("").astype(str)

            for drug in DRUGS:

                mask = series.str.contains(
                    drug,
                    case=False,
                    regex=False
                )

                if mask.any():
                    found.add(drug)

        if found:

            for drug in sorted(found):
                print("  FOUND:", drug)

        else:
            print("  No unresolved drugs found")

    except Exception as e:
        print("  SKIPPED:", type(e).__name__, str(e)[:150])

print("\n" + "=" * 70)
print("SEARCH COMPLETED")
print("=" * 70)