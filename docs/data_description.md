# all-stream-unique-database-v3: Data Description

A database of unique Gaia DR3 stellar stream members, built with the
[AstroDB Toolkit](https://github.com/astrodbtoolkit). This document describes
the source data, ingestion decisions, schema layout, and record counts.

---

## Source Data

| File | Description |
|------|-------------|
| `all_streams_unique.fits` | 80,162 rows × 40 columns; Gaia DR3 kinematics, photometry, and stream memberships compiled by Ibata et al. (2024) and associated works. 80,135 unique Gaia source IDs — 27 stars appear twice because they are members of two overlapping streams. |

The FITS file was produced by combining stream membership catalogs from 15 published works
(see [Publications](#publications) below) and cross-matching them with Gaia DR3 astrometry.
All coordinates, parallaxes, and proper motions are from Gaia DR3 (epoch J2016.0).

---

## Record Counts

| Table | Rows | Notes |
|-------|------|-------|
| Publications | 15 | One per source paper |
| Telescopes | 1 | Gaia |
| Instruments | 2 | Gaia AF (imaging), Gaia RVS (spectroscopy) |
| PhotometryFilters | 1 | Gaia G-band (`Gaia/Gaia3.G`, λ_eff = 6231 Å) |
| RegimeList | 1 | `optical` |
| AssociationList | 92 | One per stellar stream |
| ParameterList | 8 | `bp_rp`, `d_orb_kpc`, `X_kpc`, `Y_kpc`, `Z_kpc`, `dist_kpc`, `FeH`, `aFe` |
| Sources | 80,135 | One row per unique Gaia DR3 source |
| Names | 160,270 | 2 per source: `"Gaia DR3 <id>"` (primary) + raw integer `source_id` (alternate) |
| Parallaxes | 80,130 | 5 sources with NaN parallax excluded |
| ProperMotions | 80,130 | Same 5 sources excluded |
| RadialVelocities | 6,942 | Only sources with non-NaN Gaia RVS measurements |
| Photometry | 80,135 | G-band only (`phot_g_mean_mag`, 11–21 mag) |
| Associations | 80,162 | All source × stream pairs (27 duplicate stars appear twice) |
| ModeledParameters | 458,088 | 8 parameters; `dist_kpc`/`FeH`/`aFe` are sparse (see below) |

### ModeledParameters breakdown

| Parameter | Rows | Notes |
|-----------|------|-------|
| `bp_rp` | 80,135 | Gaia BP−RP colour index (all sources) |
| `d_orb_kpc` | 80,135 | Galactocentric orbital distance (all sources) |
| `X_kpc` | 80,135 | Galactocentric X coordinate (all sources) |
| `Y_kpc` | 80,135 | Galactocentric Y coordinate (all sources) |
| `Z_kpc` | 80,135 | Galactocentric Z coordinate (all sources) |
| `dist_kpc` | 55,397 | Heliocentric distance (sparse — not all stream papers provide this) |
| `FeH` | 1,967 | [Fe/H] iron abundance (sparse — only streams with spectroscopy) |
| `aFe` | 49 | [α/Fe] alpha-element abundance (very sparse) |

---

## Source Naming

Primary key in `Sources`: `"Gaia DR3 <source_id>"` where `source_id` is the Gaia DR3
integer identifier (e.g. `"Gaia DR3 1032722790379614464"`).

The raw integer `source_id` is stored as an alternate name in `Names` (e.g. `"1032722790379614464"`),
allowing lookup by either form.

---

## Ingestion Decisions

### Epoch
`epoch_year = 2016.0` for all sources. Gaia DR3 reports positions at J2016.0 (ICRS).

### Adopted flag
`adopted = True` for every measurement row. Each source has at most one measurement
per table (single-reference dataset), so every row is by definition the adopted value.

### Multi-reference rows
484 rows in the FITS file have comma-separated references (e.g. `"Ibata2024, Li2021"`).
These are stars whose stream membership was identified by two papers simultaneously.
- **FK reference**: first entry (`"Ibat24"`)
- **Second reference**: stored in the `comments` field as `"ref2: Li__21"`

### Parallax / proper motion NaN rows
5 sources have NaN parallax, proper motion, and radial velocity in the FITS file.
These sources are included in `Sources` (with coordinates) but excluded from
`Parallaxes`, `ProperMotions`, and `RadialVelocities`.

### Radial velocity errors
1,174 sources have `Vr_err = 0` in the FITS file (valid Vr but no reported uncertainty).
`rv_error` is stored as `NULL` for these rows rather than `0`.

### Duplicate sources (27 stars in two streams)
27 source IDs appear in two different stream membership lists (both retained in the
original FITS as separate rows). These stars have:
- **One `Sources` row** (first occurrence wins)
- **Two `Associations` rows** (one per stream)
- **One row each** in Parallaxes, ProperMotions, RadialVelocities, Photometry, ModeledParameters

---

## Publications

Reference shortnames follow the 4+2 convention: first 4 characters of the last name
+ 2-digit year. Short last names (≤2 chars) are padded with underscores (e.g. `Li__21`).

| Shortname | Authors | DOI |
|-----------|---------|-----|
| Awad2024 | Awad et al. 2024 | 10.1051/0004-6361/202347848 |
| Bona20 | Bonaca et al. 2020 | 10.3847/2041-8213/ab800c |
| Chan22 | Chandra et al. 2022 | 10.3847/1538-4357/ac9b4b |
| Ferg22 | Ferguson et al. 2022 | 10.3847/1538-3881/ac3492 |
| Gril19 | Grillmair 2019 | 10.3847/1538-4357/ab441d |
| Gril22 | Grillmair 2022 | 10.3847/1538-4357/ac5bd7 |
| Huan19 | Huang et al. 2019 | 10.3847/1538-4357/ab158a |
| Ibat24 | Ibata et al. 2024 | 10.3847/1538-4357/ad382d |
| Kopo23 | Koposov et al. 2023 | 10.1093/mnras/stad551 |
| Li__21 | Li et al. 2021 | 10.3847/1538-4357/abeb18 |
| Ship19 | Shipp et al. 2019 | 10.3847/1538-4357/ab44bf |
| Ship20 | Shipp et al. 2020 | 10.3847/1538-3881/abbd3a |
| Vasi21 | Vasiliev et al. 2021 | 10.1093/mnras/staa3673 |
| Yang22 | Yang et al. 2022 | 10.1051/0004-6361/202243976 |
| Yang23 | Yang et al. 2023 | 10.3847/1538-4357/acdee2 |

---

## Schema

15 tables in total. See [README.md](README.md) for per-table markdown docs.

```
Publications ──┐
Telescopes     ├── Instruments
               │
               ├── PhotometryFilters
               │
RegimeList ────┤
AssociationList┤
ParameterList  │
               │
Sources ───────┼── Names
               ├── Parallaxes
               ├── ProperMotions
               ├── RadialVelocities
               ├── Photometry
               ├── Associations
               └── ModeledParameters
```

Full schema definition: [`schema.yaml`](../schema.yaml)

---

## Build

Database built with the `astrodb-bot` Claude Code plugin (v1.2.0).
See [`astrodb-build-artifacts/workflow.md`](../astrodb-build-artifacts/workflow.md) for the
step-by-step build log and [`astrodb-build-artifacts/directions.md`](../astrodb-build-artifacts/directions.md)
for dataset-specific ingestion decisions.
