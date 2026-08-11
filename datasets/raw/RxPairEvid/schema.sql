-- RxPairEvid_50K / schema.sql
-- PostgreSQL 12+ (tested on 14)
-- Structure-only DDL for the public subset. No data is included.
-- It documents attachment points to external resources (FAERS, MedDRA, etc.)
-- without redistributing any third-party payloads.

BEGIN;

-- Keep everything namespaced
CREATE SCHEMA IF NOT EXISTS rxpairevid;

-- Recreate table to ensure shape is correct (safe on re-run)
DROP TABLE IF EXISTS rxpairevid.ddi_pairs_50k;

CREATE TABLE rxpairevid.ddi_pairs_50k (
  -- Canonical 14-char InChIKey connection layer IDs for drugs A and B
  drug_a_ik14  CHAR(14) NOT NULL,
  drug_b_ik14  CHAR(14) NOT NULL,

  -- Readable preferred names (as shipped in the CSV)
  a_name       TEXT     NOT NULL,
  b_name       TEXT     NOT NULL,

  -- Canonical pair identifier: LEAST(a,b) || '::' || GREATEST(a,b)
  pair_id      TEXT     NOT NULL,

  -- FAERS evidence summary (strict definition used in the paper)
  n_faers_reports              INTEGER          NOT NULL DEFAULT 0,  -- total reports counted for the pair
  faers_prr_max_strict         DOUBLE PRECISION,                     -- max PRR across PTs (strict filters)
  faers_ror95_lcl_max_strict   DOUBLE PRECISION,                     -- max ROR 95% LCL across PTs (strict)
  faers_pt_covered_strict      INTEGER          NOT NULL DEFAULT 0,  -- #PTs that met strict filters for this pair
  faers_best_pt_code_strict    TEXT,                                 -- MedDRA PT *code* (numeric string), not text

  -- ---------- Integrity constraints ----------
  -- Canonical ordering A ≤ B (lexicographically)
  CONSTRAINT ck_ab_order
    CHECK (drug_a_ik14 <= drug_b_ik14),

  -- pair_id must equal the canonical composition of A and B
  CONSTRAINT ck_pair_id_matches
    CHECK (
      pair_id = (LEAST(drug_a_ik14, drug_b_ik14) || '::' || GREATEST(drug_a_ik14, drug_b_ik14))
    ),

  -- Non-negative counts and signals (NULLs allowed where evidence absent)
  CONSTRAINT ck_counts_nonneg
    CHECK (n_faers_reports >= 0 AND faers_pt_covered_strict >= 0),

  CONSTRAINT ck_signals_nonneg
    CHECK (
      (faers_prr_max_strict       IS NULL OR faers_prr_max_strict       >= 0.0) AND
      (faers_ror95_lcl_max_strict IS NULL OR faers_ror95_lcl_max_strict >= 0.0)
    ),

  -- If present, best PT code must look like digits only (MedDRA code; keep column TEXT for portability)
  CONSTRAINT ck_best_pt_digits
    CHECK (faers_best_pt_code_strict IS NULL OR faers_best_pt_code_strict ~ '^[0-9]+$')
);

-- Primary/unique keys
ALTER TABLE rxpairevid.ddi_pairs_50k
  ADD CONSTRAINT pk_pairs PRIMARY KEY (drug_a_ik14, drug_b_ik14);

ALTER TABLE rxpairevid.ddi_pairs_50k
  ADD CONSTRAINT uq_pair_id UNIQUE (pair_id);

-- Helpful indexes for common analytics
CREATE INDEX IF NOT EXISTS idx_pairs_ror95
  ON rxpairevid.ddi_pairs_50k (faers_ror95_lcl_max_strict DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_pairs_prr
  ON rxpairevid.ddi_pairs_50k (faers_prr_max_strict DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_pairs_reports
  ON rxpairevid.ddi_pairs_50k (n_faers_reports DESC);

-- ---------- Column documentation (COMMENTs show up in \d+ and many GUIs) ----------
COMMENT ON TABLE  rxpairevid.ddi_pairs_50k IS
  'RxPairEvid public subset (50K). One row per drug pair (A<=B). FAERS strict signals aggregated across PTs. PT text is excluded due to MedDRA licensing; only the best PT *code* is released.';

COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.drug_a_ik14
  IS 'Drug A identifier (InChIKey connection layer, 14 chars), canonicalized so A<=B.';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.drug_b_ik14
  IS 'Drug B identifier (InChIKey connection layer, 14 chars), canonicalized so A<=B.';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.a_name
  IS 'Preferred name for drug A (for readability only).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.b_name
  IS 'Preferred name for drug B (for readability only).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.pair_id
  IS 'Deterministic pair key: LEAST(A,B)||''::''||GREATEST(A,B). Matches the CSV.';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.n_faers_reports
  IS 'Total FAERS reports contributing to the pair evidence in this release (integer, >=0).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.faers_prr_max_strict
  IS 'Maximum PRR observed across PTs under strict filters (double precision, >=0, nullable).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.faers_ror95_lcl_max_strict
  IS 'Maximum ROR lower 95% confidence bound observed across PTs under strict filters (double precision, >=0, nullable).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.faers_pt_covered_strict
  IS '# PTs that met strict filters (e.g., a_raw>=3, min thresholds) for this pair (integer, >=0).';
COMMENT ON COLUMN rxpairevid.ddi_pairs_50k.faers_best_pt_code_strict
  IS 'MedDRA Preferred Term CODE (digits only) of the PT yielding the max ROR95_LCL under strict filters. PT text omitted due to MedDRA licensing.';

-- ---------- Attachment documentation (structure only; no payloads) ----------
-- This table documents how public columns relate to external resources.
-- It contains NO ROWS in this release; it is only for documentation.
DROP TABLE IF EXISTS rxpairevid.external_attachments_doc;
CREATE TABLE rxpairevid.external_attachments_doc (
  attach_name   TEXT PRIMARY KEY,   -- e.g., 'FAERS', 'MedDRA', 'DrugBank'
  local_columns TEXT NOT NULL,      -- e.g., 'faers_* columns', 'faers_best_pt_code_strict'
  join_how      TEXT NOT NULL,      -- description of join key (e.g., 'MedDRA PT code to MedDRA PT table')
  notes         TEXT                -- licensing / usage notes
);

COMMENT ON TABLE rxpairevid.external_attachments_doc IS
  'Documentation-only table indicating where external resources can attach. No data shipped.';

-- ---------- Optional: quick sanity view (no external dependencies) ----------
DROP VIEW IF EXISTS rxpairevid.v_pairs_50k_summary;
CREATE VIEW rxpairevid.v_pairs_50k_summary AS
SELECT
  COUNT(*) AS rows_total,
  COUNT(*) FILTER (WHERE faers_ror95_lcl_max_strict IS NOT NULL) AS rows_with_ror95,
  COUNT(*) FILTER (WHERE faers_prr_max_strict       IS NOT NULL) AS rows_with_prr,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY faers_ror95_lcl_max_strict) AS ror95_p50,
  percentile_cont(0.9) WITHIN GROUP (ORDER BY faers_ror95_lcl_max_strict) AS ror95_p90
FROM rxpairevid.ddi_pairs_50k;

COMMIT;

-- ---------- How to load the CSV (example; run manually in psql) ----------
-- \copy rxpairevid.ddi_pairs_50k
--   FROM '/path/to/ddi_pairs_50k.csv'
--   CSV HEADER;
-- After loading:
-- SELECT * FROM rxpairevid.v_pairs_50k_summary;
