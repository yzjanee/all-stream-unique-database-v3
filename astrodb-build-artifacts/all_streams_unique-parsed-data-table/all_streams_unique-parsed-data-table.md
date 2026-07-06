# Column Information: all_streams_unique.fits

**File:** `all_streams_unique.fits`
**Format:** fits
**Reader:** astropy
**Rows:** 80,162
**Columns:** 40

| Column | Description | Units | Type | NaN count |
|--------|-------------|-------|------|-----------|
| `source_id` | Gaia DR3 unique source identifier | — | int64 | 0 |
| `dist` | Heliocentric distance | kpc | float64 | 24,765 |
| `dist_err` | Uncertainty on heliocentric distance | kpc | float64 | 24,927 |
| `Vr` | Line-of-sight radial velocity | km/s | float64 | 73,214 |
| `Vr_err` | Uncertainty on radial velocity | km/s | float64 | 73,214 |
| `FeH` | Iron metallicity [Fe/H] | dex | float64 | 78,195 |
| `FeH_err` | Uncertainty on [Fe/H] | dex | float64 | 78,195 |
| `aFe` | Alpha-to-iron abundance ratio [α/Fe] | dex | float64 | 80,113 |
| `aFe_err` | Uncertainty on [α/Fe] | dex | float64 | 80,113 |
| `p_mem` | Stream membership probability | — | float64 | 79,913 |
| `ra` | Right ascension (ICRS, J2016.0) | deg | float64 | 0 |
| `ra_error` | Uncertainty on right ascension | mas | float32 | 0 |
| `dec` | Declination (ICRS, J2016.0) | deg | float64 | 0 |
| `dec_error` | Uncertainty on declination | mas | float32 | 0 |
| `parallax` | Parallax | mas | float64 | 5 |
| `parallax_error` | Uncertainty on parallax | mas | float32 | 5 |
| `parallax_over_error` | Parallax significance (parallax / parallax_error) | — | float32 | 5 |
| `pm` | Total proper motion magnitude | mas/yr | float32 | 5 |
| `pmra` | Proper motion in right ascension (includes cos δ) | mas/yr | float64 | 5 |
| `pmra_error` | Uncertainty on pmra | mas/yr | float32 | 5 |
| `pmdec` | Proper motion in declination | mas/yr | float64 | 5 |
| `pmdec_error` | Uncertainty on pmdec | mas/yr | float32 | 5 |
| `ra_dec_corr` | Correlation coefficient: ra × dec | — | float32 | 0 |
| `ra_parallax_corr` | Correlation coefficient: ra × parallax | — | float32 | 5 |
| `ra_pmra_corr` | Correlation coefficient: ra × pmra | — | float32 | 5 |
| `ra_pmdec_corr` | Correlation coefficient: ra × pmdec | — | float32 | 5 |
| `dec_parallax_corr` | Correlation coefficient: dec × parallax | — | float32 | 5 |
| `dec_pmra_corr` | Correlation coefficient: dec × pmra | — | float32 | 5 |
| `dec_pmdec_corr` | Correlation coefficient: dec × pmdec | — | float32 | 5 |
| `parallax_pmra_corr` | Correlation coefficient: parallax × pmra | — | float32 | 5 |
| `parallax_pmdec_corr` | Correlation coefficient: parallax × pmdec | — | float32 | 5 |
| `pmra_pmdec_corr` | Correlation coefficient: pmra × pmdec | — | float32 | 5 |
| `phot_g_mean_mag` | Gaia G-band mean magnitude | mag | float32 | 0 |
| `bp_rp` | Gaia BP minus RP color index | mag | float32 | 0 |
| `name` | Stellar stream name | — | str | 0 |
| `reference` | Discovery/membership reference(s); comma-separated for multi-ref rows | — | str | 0 |
| `d_orb` | Orbital distance from Galactic center | kpc | float64 | 0 |
| `X` | Galactocentric X coordinate | kpc | float64 | 0 |
| `Y` | Galactocentric Y coordinate | kpc | float64 | 0 |
| `Z` | Galactocentric Z coordinate | kpc | float64 | 0 |

## Notes

- No embedded FITS descriptions — all descriptions inferred from column names and Gaia DR3 data model.
- `[-]` unit in FITS header for `FeH` / `FeH_err` is non-standard; treated as dimensionless (dex).
- `p_mem` has only **249 non-NaN rows** out of 80,162 — membership probability is present only for a small subset of streams.
- `parallax` / proper motion columns have 5 NaN rows (same 5 stars) — ingest as-is per meeting decision.
- `reference` column has 484 multi-reference rows (comma-separated). First value is the FK; second goes in `comments`.
- 92 unique stream names. 15 unique first-author references.
- Gaia DR3 positions and proper motions are at epoch **J2016.0** — set `epoch_year = 2016.0` in Sources.
