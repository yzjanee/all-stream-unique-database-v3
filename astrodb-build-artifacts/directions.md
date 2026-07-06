# all-stream-unique-database-v3: Directions Document

This document records dataset-specific decisions, schema choices, and ingestion notes from
planning meetings. It is the authoritative reference for build and ingest skills.

---

## Source data

| File | Description |
|------|-------------|
| `all_streams_unique.fits` | 80,162 rows × 40 columns; unique Gaia DR3 stream members (one row per star per stream; 80,135 unique source IDs; 27 stars assigned to two overlapping streams by Ibata2024). |

---

## Meeting notes (Cecilia, 2026-07-06)

### Schema and table decisions

- **FeH and aFe** go into `ModeledParameters` (not a dedicated abundance table).
- **Each row in the FITS file is a single star** in a single stream. The unit of data is one
  star–stream membership.
- **Start with the unique-stars table first** (`all_streams_unique.fits`) in a separate table.
  The full-memberships table (`all_stream.fits`) may be ingested later.
- **Schema is extensible**: the initial schema is defined from this data table. Additional
  attributes (e.g. new measurements) can be added to existing tables later without rebuilding
  from scratch.

### Column-to-table mapping decisions

| Column(s) | Table | Notes |
|-----------|-------|-------|
| `source_id` | `Sources` (PK) + `Names` | Primary key as `"Gaia DR3 <source_id>"`; raw integer stored as alternate name |
| `name` | `AssociationList` + `Associations` | Stream name (92 unique streams) |
| `reference` | `Publications` + all tables | First comma-separated value is the FK; second goes in `comments` |
| `p_mem` | `Associations` | Membership probability |
| `parallax`, `parallax_error` | `Parallaxes` | Ingest bad (negative) parallaxes — do not filter |
| `pmra`, `pmdec`, `*_error`, `*_corr` | `ProperMotions` | |
| `Vr`, `Vr_err` | `RadialVelocities` | ~6,942 non-NaN rows |
| `phot_g_mean_mag` | `Photometry` | band = `Gaia/Gaia3.G` |
| `bp_rp` | `ModeledParameters` | parameter = `bp_rp` |
| `FeH`, `aFe`, `*_err` | `ModeledParameters` | |
| `dist`, `dist_err` | `ModeledParameters` | parameter = `dist_kpc`; keep even with NaNs |
| `d_orb` | `ModeledParameters` | Include (overrides earlier "ignore" decision); reference = the paper |
| `X`, `Y`, `Z` | `ModeledParameters` | Galactocentric coordinates; include |

### Ingestion rules

- **Multiple memberships / multi-reference rows**: 484 FITS rows have comma-separated references
  (e.g. `"Bonaca2020, Ibata2024"`). Use the first as the FK everywhere. Store the second
  reference in the `comments` field of the relevant table row.
- **epoch_year**: Ingest `epoch_year` for sources (needed for proper motion epoch tracking and
  Gaia index). Add epoch to Sources `ra_index`.
- **adopted column**: For single-measurement sources (most stars have exactly one measurement
  per table), set `adopted = True` in all measurement tables.
- **Ingest bad parallaxes**: Yes — do not filter negative or large-uncertainty parallaxes.
- **Distances**: Keep `dist` in `ModeledParameters` alongside `d_orb`.
- **Gaia match**: Use `gaia_id` (raw source_id integer) for matching; use our own `gaia_match`
  if the Gaia source ID is available.
- **Telescopes and Instruments**: Populate both lookup tables for Gaia before ingesting Photometry.

### p_membership

- If a star has only one stream membership, store one Associations row.
- If a star has multiple memberships (different streams), store one row per (source, association)
  pair — the Associations PK handles this.

### Proper motion

- ProperMotions will be updated when new Gaia data arrives. A dedicated skill
  (`astrodb-update-gaia`) should be written to handle this workflow.
- When proper motion data is updated, a new row is added (not an overwrite), and the old row is
  retained with `adopted = False`; the new row gets `adopted = True`.

### Documentation

- Create step-by-step documentation for the stream database build workflow using skills,
  including the exact prompts used. This will be saved in `astrodb-build-artifacts/workflow.md`
  and will serve as a companion tutorial.

---

## Lookup table load order (database.toml)

FK dependencies require this order:
```toml
lookup_tables = [
    "Publications",
    "Telescopes",
    "Instruments",
    "PhotometryFilters",
    "RegimeList",
    "AssociationList",
    "ParameterList"
]
```

---

## Known issues / gotchas (carried forward from v2)

- **`find_publication` dedup**: Always use `find_publication(db, doi=doi)` (DOI only), never
  `find_publication(db, reference=reference, doi=doi)`. The reference-based matching uses
  substring year matching that produces false positives (e.g. `"Shipp2019"` matches a query for
  `"Shipp2020"`).
- **`search_db=False` in `ingest_source`**: Required when calling on an empty or near-empty
  database. The `astrodbkit.query_region` function fails with a `KeyError` on an empty DataFrame.
  Manual deduplication via a `seen_source_ids` set replaces the DB-side search.
- **`db.save_database("data/")`**: Requires the directory argument.
- **27 duplicate source_ids**: Stars Ibata2024 assigned to two overlapping streams.
  Deduplicated for Sources/Names/Parallaxes/ProperMotions/Photometry/ModeledParameters (first
  occurrence wins). Both `(source, stream)` pairs go into Associations.
