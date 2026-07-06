# all-stream-unique-database-v3: Build Workflow

Step-by-step log of how v3 was built, with exact prompts used. See also `directions.md` for
dataset-specific decisions.

---

## Source data

| File | Description |
|------|-------------|
| `all_streams_unique.fits` | 80,162 rows × 40 columns; Gaia DR3 stellar stream members (80,135 unique source IDs). Located in the v2 repo at `all-stream-unique-database-v2/`. |

---

## Tool

Built with the `astrodb-bot` Claude Code plugin (v1.2.0+, includes SESAME/SIMBAD name check in ingest-sources). All steps ran in the `all-stream-unique-database-v3/` directory.

---

## Step 1: `astrodb-build-setup` — Repository setup

**Prompt:**
> Create a new AstroDB for Gaia DR3 stellar stream members. Repo URL: https://github.com/yzjanee/all-stream-unique-database-v3

**What happened:**
- Merged latest upstream astrodb_bot skills (v1.2.0 — adds SESAME/SIMBAD check in ingest-sources)
- Confirmed repo was cloned from astrodb-template-db template
- Removed stale template files: `docs/figures/schema_erd.png`, `docs/schema/*.md`
- Removed template source data: `data/source/*.json`
- Set `db_name = "all_streams_unique_v3"` in `database.toml`
- Updated README title and description
- Created `astrodb-build-artifacts/` and `astrodb-ingest-artifacts/` directories
- Saved meeting notes as `astrodb-build-artifacts/directions.md`
- Updated `CLAUDE.md`: added build-artifacts folder note, GitHub token requirement, minimized diff from template
- Cleared template reference JSON files

---

## Step 2: `astrodb-build-parse-table` — Parse the FITS file

**Prompt:**
> `/astrodb-build-parse-table` Parse `all_streams_unique.fits`

**Output:**
- `astrodb-build-artifacts/all_streams_unique-parsed-data-table/all_streams_unique-parsed-data-table.md`
- `astrodb-build-artifacts/all_streams_unique-parsed-data-table/all_streams_unique-parsed-data-table.html`
- `astrodb-build-artifacts/astrodb-parse-result.json`

**Key findings:**
- 80,162 rows × 40 columns
- `p_mem` has only 249 non-NaN rows (membership probability sparse)
- 484 rows have comma-separated references
- 5 rows with NaN parallax/PM (same 5 stars) — ingest anyway
- Gaia DR3 epoch is J2016.0 → `epoch_year = 2016.0`

---

## Step 3: `astrodb-build-schema-match` — Map columns to AstroDB tables

**Prompt:**
> `/astrodb-build-schema-match` Apply Cecilia meeting decisions (see directions.md)

**Output:**
- `astrodb-build-artifacts/all_streams_unique-schema-match/all_streams_unique-schema-match.md`

**Key decisions:**
- `source_id` → Sources PK as `"Gaia DR3 <source_id>"` + Names alternate name (raw int)
- `name` (stream) → AssociationList + Associations
- `reference` → first FK; second goes in `comments`
- `pmra`, `pmdec` → ProperMotions (`pm_ra`, `pm_dec`) — fixed v2 field name error
- `pmra_pmdec_corr` → new `pmra_pmdec_corr` field added to ProperMotions
- `d_orb`, `X`, `Y`, `Z` → ModeledParameters (meeting decision: include)
- `epoch_year = 2016.0` stored in Sources
- `adopted = True` for all single measurements

---

## Step 4: `astrodb-build-schema-generate` — Write schema.yaml

**What happened:**
- Wrote v3 `schema.yaml` (15 tables: removed Versions, Positions, CompanionList,
  CompanionRelationships, CompanionParameters, SourceTypes, SourceTypeList, Morphology,
  RotationalParameters, Spectra from template)
- Added `pmra_pmdec_corr` field to ProperMotions
- Simplified ModeledParameters PK to `(source, parameter, reference)` — no `model` field
- Passed `felis validate schema.yaml` ✓
- Updated `database.toml` lookup table order

---

## Step 5: `astrodb-build-create-db` — Create the database

**What happened:**
- Created `all_streams_unique_v3.sqlite` (196 KB, empty)
- Updated test suite (14 tests):
  - conftest.py: updated db filename
  - test_contents.py: 15 tables (not 25)
  - test_contents_sources.py: added epoch_year test
  - test_contents_kinematics.py: counts = 0 (empty DB)
  - test_contents_parameters.py: added associations test
  - test_database.py: add publication before inserting source (FK fix)
  - Removed test_contents_morphology.py, test_contents_positions.py
- All 14 tests pass ✓

---

## Step 6: `astrodb-ingest-publications` — Ingest 15 publications

**Script:** `astrodb-ingest-artifacts/ingest_all_streams_unique_publications.py`

**What happened:**
- Ingested 15 publications with `ignore_ads=True` (no ADS_TOKEN)
- Reference naming: 4-char last name + 2-digit year (e.g., `Li__21` for 2-char names)
- Dry run (SAVE_DB=False): 15 added, 0 already present, 0 failed ✓
- Live run (SAVE_DB=True): saved to `data/reference/Publications.json` ✓
- All 14 tests pass ✓

**References ingested:** Awad2024, Bona20, Chan22, Ferg22, Gril19, Gril22, Huan19, Ibat24,
Kopo23, Li__21, Ship19, Ship20, Vasi21, Yang22, Yang23

---

## Step 7: `astrodb-ingest-sources` — Ingest 80,135 sources

**Script:** `astrodb-ingest-artifacts/ingest_all_streams_unique_sources.py`

**What happened:**
- SESAME/SIMBAD name check (skill Step 1.5): skipped — source names are systematic
  Gaia DR3 IDs; 80k queries would take hours and most stream candidates are not in SIMBAD
- Source name format: `"Gaia DR3 {source_id}"` (PK); raw integer source_id added to Names
- `epoch_year = 2016.0` for all sources (Gaia DR3 reference epoch J2016.0)
- FITS full reference names (e.g. `Bonaca2020`) mapped to v3 shortnames (e.g. `Bona20`)
  via `REFERENCE_MAP` dict; `search_db=False` to skip astrodbkit query_region overhead
- 27 duplicate source_ids (stars in two streams) deduplicated via `seen_source_ids` set
- Dry run: 80,135 sources ingested, 80,135 alternate names added, 0 skipped ✓
- Live run: saved to `data/source/` (80,135 JSON files) ✓
- Updated `tests/test_contents_sources.py`: expects 80,135 sources, 160,270 names
- All 14 tests pass ✓

---

## Step 8: Measurements ingestion — 6 data tables

**Script:** `astrodb-ingest-artifacts/ingest_all_streams_unique_measurements.py`

**What happened:**

Lookup tables populated first (required before FK constraints can be satisfied):
- Telescopes: `Gaia` (reference `Ibat24`)
- Instruments: `Gaia AF` (imaging), `Gaia RVS` (spectroscopy)
- PhotometryFilters: `Gaia/Gaia3.G` (λ_eff = 6231 Å)
- RegimeList: `optical`
- AssociationList: 92 streams (references mapped to v3 shortnames per stream discoverer)
- ParameterList: 8 parameters (`bp_rp`, `d_orb_kpc`, `X_kpc`, `Y_kpc`, `Z_kpc`,
  `dist_kpc`, `FeH`, `aFe`)

Data tables (one pass over FITS, bulk-inserted via SQLAlchemy):

| Table | Rows | Notes |
|-------|------|-------|
| Parallaxes | 80,130 | 5 NaN-parallax sources excluded |
| ProperMotions | 80,130 | `pm_ra`/`pm_dec`/`pmra_pmdec_corr` only (v3 schema simplified) |
| RadialVelocities | 6,942 | 73,193 NaN-Vr sources excluded; `Vr_err==0` stored as NULL |
| Photometry | 80,135 | G-band only (`phot_g_mean_mag`); deduped by source_id |
| Associations | 80,162 | All source×stream pairs; 27 duplicate stars appear twice |
| ModeledParameters | 458,088 | 8 params; `dist_kpc`/`FeH`/`aFe` sparse (not all papers provide) |

All rows: `adopted = True`. 484 multi-ref rows store second reference as `"ref2: <shortname>"`
in the `comments` field.

- Dry run: all 6 tables inserted cleanly, 0 errors ✓
- Live run: saved to `data/source/` + `data/reference/` ✓
- Updated `tests/test_contents_kinematics.py` and `tests/test_contents_parameters.py`
  with exact row counts
- All 14 tests pass ✓

**Gotcha:** `all_streams_unique_v3.sqlite` grew to ~179 MB with full data — exceeds GitHub's
100 MB file size limit. Added `*.sqlite` to `.gitignore`; sqlite is now a local-only generated
artifact rebuilt by `build_db_from_json` from the JSON data files.

---

## Step 9: Documentation

**What happened:**
- Regenerated `docs/schema/*.md` (15 files) from `schema.yaml` via `scripts/build_schema_docs.py`
- `docs/README.md` updated: lists only v3's 15 tables, no ERD reference
- Created `docs/data_description.md`: record counts, source naming, ingestion decisions,
  publications table
- Updated top-level `README.md`: removed broken ERD image link, added link to
  `docs/data_description.md`

---

## Remaining / future work

- Open GitHub issue: proper motion accuracy discussion + `pmra_pmdec_corr` field rationale
- Write `astrodb-update-gaia` skill for future Gaia data refresh workflow
