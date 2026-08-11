# RxPairEvid-50K public subset

This repository contains the license-clean 50k public subset from the RxPairEvid dataset: a machine-learning-ready table of drug–drug pairs with FAERS-derived disproportionality and per-pair rationale fields. Third-party payloads (DrugBank, KEGG, PDBbind, MedDRA text) are not redistributed here.

## What’s inside
- ddi_pairs_50k.csv
- schema.sql
- codebook.md
- audit_subset_signal_quantiles.csv
- audit_subset_strata_counts.csv
- provenance.md
- checksums.txt
- LICENSE.txt

## Quick start: load in Python (pandas)
```python
import pandas as pd
df = pd.read_csv("ddi_pairs_50k.csv")
print(df.shape)
print(df.head())
```

## Quick start: load in DuckDB (fast SQL over CSV)
```bash
duckdb :memory: "CREATE TABLE rxpairevid_50k AS SELECT * FROM read_csv_auto('ddi_pairs_50k.csv'); DESCRIBE rxpairevid_50k; SELECT * FROM rxpairevid_50k LIMIT 5;"
```

## Load in PostgreSQL
Option A: use the DDL we provide.
```bash
createdb rxpairevid
psql -d rxpairevid -f schema.sql
psql -d rxpairevid -c "\COPY ddi_pairs_50k FROM 'ddi_pairs_50k.csv' CSV HEADER"
```

Option B: create a table on the fly (no constraints) after inspecting column names.
```sql
-- inside psql after \copy to a staging table:
-- CREATE TABLE rxpairevid_50k AS SELECT * FROM rxpairevid_50k_stage;
```

## License
- CC BY 4.0 for the files in this repository authored by us.
- No redistribution of third-party payloads (DrugBank, KEGG, PDBbind, MedDRA text).
- MedDRA concept codes may appear; MedDRA text is not included here.

## How to cite
- Article: RxPairEvid-50K: machine-learning-ready drug–drug pair evidence from FAERS. Data in Brief, 2025.
- Dataset: RxPairEvid-50K public subset. 
