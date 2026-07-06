# Schema Match: all_streams_unique.fits → AstroDB Tables

**Source:** `all_streams_unique.fits` (80,162 rows, 40 columns)
**Decisions from:** meeting notes 2026-07-06 (see `directions.md`)

| Column | Description | Units | Type | DB Table | DB Field | Confidence | Notes |
|--------|-------------|-------|------|----------|----------|------------|-------|
| `source_id` | Gaia DR3 source identifier | — | int64 | Sources + Names | `source` (PK as `"Gaia DR3 <source_id>"`); raw int in `Names.other_name` | High | Primary source key; also stored as alternate name |
| `ra` | Right ascension (J2016.0) | deg | float64 | Sources | `ra_deg` | High | Gaia DR3 epoch J2016.0 → `epoch_year = 2016.0` |
| `dec` | Declination (J2016.0) | deg | float64 | Sources | `dec_deg` | High | |
| `ra_error` | Uncertainty on RA | mas | float32 | Sources | `ra_error` (new field) | Proposed (new field) | Not in template Sources; needed for Gaia astrometry |
| `dec_error` | Uncertainty on dec | mas | float32 | Sources | `dec_error` (new field) | Proposed (new field) | Not in template Sources |
| `name` | Stellar stream name | — | str | AssociationList + Associations | `association` (PK in AssociationList); FK in `Associations.association` | High | 92 unique streams |
| `reference` | Membership/discovery reference | — | str | Publications + all tables | `reference` (FK); second ref → `comments` | High | 484 multi-ref rows; first ref = FK, second ref in comments |
| `p_mem` | Membership probability | — | float64 | Associations | `membership_probability` (new field) | High | Only 249 non-NaN rows; store as nullable float |
| `parallax` | Parallax | mas | float64 | Parallaxes | `parallax_mas` | High | Ingest all including negative values |
| `parallax_error` | Uncertainty on parallax | mas | float32 | Parallaxes | `parallax_error` | High | |
| `parallax_over_error` | Parallax significance | — | float32 | Parallaxes | `parallax_over_error` (new field) | Proposed (new field) | Useful quality indicator; add to Parallaxes |
| `pmra` | Proper motion RA (×cos δ) | mas/yr | float64 | ProperMotions | `mu_ra` | High | |
| `pmra_error` | Uncertainty on pmra | mas/yr | float32 | ProperMotions | `mu_ra_error` | High | |
| `pmdec` | Proper motion dec | mas/yr | float64 | ProperMotions | `mu_dec` | High | |
| `pmdec_error` | Uncertainty on pmdec | mas/yr | float32 | ProperMotions | `mu_dec_error` | High | |
| `ra_dec_corr` | Correlation RA×dec | — | float32 | ProperMotions | `correlation_ra_dec` (new field) | Proposed (new field) | Gaia astrometric correlation |
| `ra_parallax_corr` | Correlation RA×parallax | — | float32 | ProperMotions | `correlation_ra_parallax` (new field) | Proposed (new field) | |
| `ra_pmra_corr` | Correlation RA×pmra | — | float32 | ProperMotions | `correlation_ra_pmra` (new field) | Proposed (new field) | |
| `ra_pmdec_corr` | Correlation RA×pmdec | — | float32 | ProperMotions | `correlation_ra_pmdec` (new field) | Proposed (new field) | |
| `dec_parallax_corr` | Correlation dec×parallax | — | float32 | ProperMotions | `correlation_dec_parallax` (new field) | Proposed (new field) | |
| `dec_pmra_corr` | Correlation dec×pmra | — | float32 | ProperMotions | `correlation_dec_pmra` (new field) | Proposed (new field) | |
| `dec_pmdec_corr` | Correlation dec×pmdec | — | float32 | ProperMotions | `correlation_dec_pmdec` (new field) | Proposed (new field) | |
| `parallax_pmra_corr` | Correlation parallax×pmra | — | float32 | ProperMotions | `correlation_parallax_pmra` (new field) | Proposed (new field) | |
| `parallax_pmdec_corr` | Correlation parallax×pmdec | — | float32 | ProperMotions | `correlation_parallax_pmdec` (new field) | Proposed (new field) | |
| `pmra_pmdec_corr` | Correlation pmra×pmdec | — | float32 | ProperMotions | `mu_ra_mu_dec_corr` | High | Standard AstroDB field name |
| `pm` | Total PM magnitude | mas/yr | float32 | ProperMotions | `mu_tot` (new field) | Proposed (new field) | Not in template; add for completeness |
| `Vr` | Radial velocity | km/s | float64 | RadialVelocities | `rv_kms` | High | 73,214 NaN → only 6,948 rows ingested |
| `Vr_err` | Uncertainty on Vr | km/s | float64 | RadialVelocities | `rv_error` | High | |
| `phot_g_mean_mag` | Gaia G magnitude | mag | float32 | Photometry | `magnitude` | High | band = `Gaia/Gaia3.G`; telescope = Gaia |
| `bp_rp` | Gaia BP−RP color | mag | float32 | ModeledParameters | `value` (parameter = `bp_rp`) | High | Color index, not a standard photometry band |
| `FeH` | [Fe/H] metallicity | dex | float64 | ModeledParameters | `value` (parameter = `FeH`) | High | 78,195 NaN → sparse |
| `FeH_err` | Uncertainty on [Fe/H] | dex | float64 | ModeledParameters | `error` (parameter = `FeH`) | High | |
| `aFe` | [α/Fe] abundance | dex | float64 | ModeledParameters | `value` (parameter = `aFe`) | High | 80,113 NaN → very sparse |
| `aFe_err` | Uncertainty on [α/Fe] | dex | float64 | ModeledParameters | `error` (parameter = `aFe`) | High | |
| `dist` | Heliocentric distance | kpc | float64 | ModeledParameters | `value` (parameter = `dist_kpc`) | High | 24,765 NaN |
| `dist_err` | Uncertainty on distance | kpc | float64 | ModeledParameters | `error` (parameter = `dist_kpc`) | High | |
| `d_orb` | Orbital distance from GC | kpc | float64 | ModeledParameters | `value` (parameter = `d_orb_kpc`) | User-assigned | Meeting decision: include in ModeledParameters |
| `X` | Galactocentric X | kpc | float64 | ModeledParameters | `value` (parameter = `X_kpc`) | User-assigned | |
| `Y` | Galactocentric Y | kpc | float64 | ModeledParameters | `value` (parameter = `Y_kpc`) | User-assigned | |
| `Z` | Galactocentric Z | kpc | float64 | ModeledParameters | `value` (parameter = `Z_kpc`) | User-assigned | |

## Lookup Table Checklist

| Lookup Table | Entries needed | Source |
|---|---|---|
| Publications | 15 shortnames → resolve to DOI/bibcode | first-ref values from `reference` column |
| Telescopes | `Gaia` | Gaia satellite |
| Instruments | `Gaia` | Gaia astrometric instrument |
| PhotometryFilters | `Gaia/Gaia3.G` | SVO Filter Profile Service |
| RegimeList | `optical` | for Gaia G band |
| AssociationList | 92 stream names | `name` column |
| ParameterList | `bp_rp`, `FeH`, `aFe`, `dist_kpc`, `d_orb_kpc`, `X_kpc`, `Y_kpc`, `Z_kpc` | 8 parameters |

## Proposed Schema Additions (new fields vs template)

These require updates to `schema.yaml` before ingestion can proceed:

| Table | New Field | Type | Units | Notes |
|-------|-----------|------|-------|-------|
| Sources | `ra_error` | float | mas | RA uncertainty from Gaia |
| Sources | `dec_error` | float | mas | Dec uncertainty from Gaia |
| Parallaxes | `parallax_over_error` | float | — | Gaia quality indicator |
| ProperMotions | `correlation_ra_dec` | float | — | Astrometric correlation |
| ProperMotions | `correlation_ra_parallax` | float | — | |
| ProperMotions | `correlation_ra_pmra` | float | — | |
| ProperMotions | `correlation_ra_pmdec` | float | — | |
| ProperMotions | `correlation_dec_parallax` | float | — | |
| ProperMotions | `correlation_dec_pmra` | float | — | |
| ProperMotions | `correlation_dec_pmdec` | float | — | |
| ProperMotions | `correlation_parallax_pmra` | float | — | |
| ProperMotions | `correlation_parallax_pmdec` | float | — | |
| ProperMotions | `mu_tot` | float | mas/yr | Total PM magnitude |
| Associations | `membership_probability` | float | — | Stream membership probability (nullable) |
