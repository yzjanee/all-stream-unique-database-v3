"""
Ingest all measurement tables for all_streams_unique_v3.

Order:
  1. Lookup tables: Telescopes, Instruments, PhotometryFilters, RegimeList,
                    AssociationList (92 streams), ParameterList (8 params)
  2. Data tables (bulk inserts):
     - Parallaxes        (~80,157 rows; 5 NaN excluded)
     - ProperMotions     (~80,157 rows; same 5 excluded)
     - RadialVelocities  (~6,948 rows; NaN Vr excluded; Vr_err==0 stored as None)
     - Photometry        (80,135 rows; deduped by source_id)
     - Associations      (80,162 rows; all unique (source, stream) pairs)
     - ModeledParameters (~454k rows across 8 parameters)

Reference handling:
  FITS stores full names (e.g. "Bonaca2020"). REFERENCE_MAP translates to
  v3 shortnames (e.g. "Bona20"). For the 484 multi-reference rows
  ("Ibata2024, Li2021"), first ref is the FK; second ref is stored in comments.

All measurement rows get adopted=True (single measurement per source).
"""

import logging
import numpy as np
from astropy.table import Table
from sqlalchemy import insert as sa_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.automap import automap_base

from astrodb_utils import build_db_from_json

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = True  # Set to True after successful dry run to persist changes

SETTINGS_FILE = "database.toml"
TABLE_PATH = "../all-stream-unique-database-v2/all_streams_unique.fits"

# FITS reference values → Publications shortnames (v3 4+2 convention)
REFERENCE_MAP = {
    "Awad2024":      "Awad2024",
    "Bonaca2020":    "Bona20",
    "Chandra2022":   "Chan22",
    "Ferguson2022":  "Ferg22",
    "Grillmair2019": "Gril19",
    "Grillmair2022": "Gril22",
    "Huang2019":     "Huan19",
    "Ibata2024":     "Ibat24",
    "Koposov2023":   "Kopo23",
    "Li2021":        "Li__21",
    "Shipp2019":     "Ship19",
    "Shipp2020":     "Ship20",
    "Vasiliev2021":  "Vasi21",
    "Yang2022":      "Yang22",
    "Yang2023":      "Yang23",
}


def first_ref(raw):
    """Return the mapped shortname for the first ref in a comma-separated string."""
    return REFERENCE_MAP[str(raw).strip().split(",")[0].strip()]


def second_ref(raw):
    """Return the mapped shortname for the second ref, or None if single-ref."""
    parts = [p.strip() for p in str(raw).strip().split(",")]
    if len(parts) < 2:
        return None
    return REFERENCE_MAP.get(parts[1])


def f(v):
    """Convert to float, returning None for NaN."""
    x = float(v)
    return None if np.isnan(x) else x


# ── Load data ──────────────────────────────────────────────────────────────────
data = Table.read(TABLE_PATH, format="fits")
logger.info(f"Loaded {len(data)} rows from {TABLE_PATH}")

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOOKUP TABLES
# ══════════════════════════════════════════════════════════════════════════════

Telescopes        = Base.classes.Telescopes
Instruments       = Base.classes.Instruments
PhotometryFilters = Base.classes.PhotometryFilters
RegimeList        = Base.classes.RegimeList
AssociationList   = Base.classes.AssociationList
ParameterList     = Base.classes.ParameterList


def insert_or_skip(session, obj):
    try:
        session.add(obj)
        session.commit()
    except IntegrityError:
        session.rollback()


with db.session as session:
    # Telescopes
    insert_or_skip(session, Telescopes(
        telescope="Gaia",
        description="ESA Gaia space observatory (Gaia DR3)",
        reference="Ibat24",
    ))

    # Instruments — Gaia photometric imager (astrometry + G-band) and RVS
    insert_or_skip(session, Instruments(
        instrument="Gaia AF",
        mode="imaging",
        telescope="Gaia",
        description="Gaia Astrometric Field — astrometry and G-band photometry",
        reference="Ibat24",
    ))
    insert_or_skip(session, Instruments(
        instrument="Gaia RVS",
        mode="spectroscopy",
        telescope="Gaia",
        description="Gaia Radial Velocity Spectrometer",
        reference="Ibat24",
    ))

    # PhotometryFilters — Gaia G-band (SVO: Gaia/Gaia3.G)
    insert_or_skip(session, PhotometryFilters(
        band="Gaia/Gaia3.G",
        ucd="em.opt",
        effective_wavelength_angstroms=6231.08,
        width_angstroms=1381.21,
    ))

    # RegimeList
    insert_or_skip(session, RegimeList(
        regime="optical",
        description="Optical wavelength regime (~3000–10000 Å)",
    ))

    # ParameterList — 8 modeled parameters
    params = [
        ("FeH",       "[Fe/H] iron abundance relative to solar"),
        ("aFe",       "[alpha/Fe] alpha-element abundance relative to solar"),
        ("dist_kpc",  "Heliocentric distance"),
        ("bp_rp",     "Gaia DR3 BP-RP colour index"),
        ("d_orb_kpc", "Galactocentric orbital distance"),
        ("X_kpc",     "Galactocentric X coordinate (right-handed, X toward Sun)"),
        ("Y_kpc",     "Galactocentric Y coordinate"),
        ("Z_kpc",     "Galactocentric Z coordinate (Z toward North Galactic Pole)"),
    ]
    for param, desc in params:
        insert_or_skip(session, ParameterList(parameter=param, description=desc))

    # AssociationList — 92 unique stellar streams
    # References: first paper to identify/characterise each stream
    stream_refs = {
        "300S": "Ibat24", "ATLAS-Aliqa Uma": "Li__21", "C-10": "Ibat24",
        "C-11": "Ibat24", "C-12": "Ibat24", "C-13": "Ibat24",
        "C-19": "Ibat24", "C-20": "Ibat24", "C-22": "Ibat24",
        "C-23": "Ibat24", "C-24": "Ibat24", "C-25": "Ibat24",
        "C-7": "Ibat24", "C-9": "Ibat24", "Cetus-Palca": "Li__21",
        "Elqui": "Ship19", "GD-1": "Ibat24", "Gaia-1": "Ibat24",
        "Gaia-11": "Ibat24", "Gaia-12": "Ibat24", "Gaia-6": "Ibat24",
        "Gaia-7": "Ibat24", "Gaia-8": "Ibat24", "Gaia-9": "Ibat24",
        "Hrid": "Ibat24", "Hydrus": "Ibat24", "Indus": "Ibat24",
        "Jet": "Ferg22", "Jhelum": "Awad2024", "Kshir": "Ibat24",
        "Kwando": "Ibat24", "Wukong": "Ibat24", "Leiptr": "Ibat24",
        "M2": "Gril22", "M3": "Yang23", "M30": "Ibat24",
        "M5": "Gril19", "M68": "Ibat24", "M92": "Ibat24",
        "NGC 1261": "Ibat24", "NGC 1851": "Ibat24", "NGC 2298": "Ibat24",
        "NGC 2808": "Ibat24", "NGC 288": "Ibat24", "NGC 3201": "Ibat24",
        "NGC 5466": "Ibat24", "NGC 5824": "Yang22", "NGC 6101": "Ibat24",
        "NGC 6397": "Ibat24", "NGC 7492": "Ibat24", "New-1": "Ibat24",
        "New-10": "Ibat24", "New-11": "Ibat24", "New-12": "Ibat24",
        "New-13": "Ibat24", "New-14": "Ibat24", "New-15": "Ibat24",
        "New-16": "Ibat24", "New-17": "Ibat24", "New-18": "Ibat24",
        "New-19": "Ibat24", "New-2": "Ibat24", "New-20": "Ibat24",
        "New-21": "Ibat24", "New-22": "Ibat24", "New-23": "Ibat24",
        "New-24": "Ibat24", "New-25": "Ibat24", "New-26": "Ibat24",
        "New-27": "Ibat24", "New-3": "Ibat24", "New-4": "Ibat24",
        "New-5": "Ibat24", "New-6": "Ibat24", "New-7": "Ibat24",
        "New-8": "Ibat24", "New-9": "Ibat24", "Omega Centauri": "Ibat24",
        "Ophiuchus": "Ibat24", "Orphan-Chenab": "Kopo23",
        "Palomar 13": "Ship20", "Palomar 5": "Ibat24",
        "Phlegethon": "Ibat24", "Phoenix": "Ibat24", "SGP-S": "Ibat24",
        "Sagittarius": "Vasi21", "Slidr": "Ibat24", "Spectre": "Chan22",
        "Sylgr": "Ibat24", "Tucana III": "Ibat24", "Turranburra": "Ship19",
        "Ylgr": "Ibat24",
    }
    for stream, ref in stream_refs.items():
        insert_or_skip(session, AssociationList(
            association=stream,
            association_type="stellar_stream",
            reference=ref,
        ))

logger.info("Lookup tables populated")

# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA TABLES — one pass to build all record lists, then bulk insert
# ══════════════════════════════════════════════════════════════════════════════

parallaxes_tbl = db.metadata.tables["Parallaxes"]
pm_tbl         = db.metadata.tables["ProperMotions"]
rv_tbl         = db.metadata.tables["RadialVelocities"]
phot_tbl       = db.metadata.tables["Photometry"]
assoc_tbl      = db.metadata.tables["Associations"]
modeled_tbl    = db.metadata.tables["ModeledParameters"]

parallax_rows = []
pm_rows       = []
rv_rows       = []
phot_rows     = []
assoc_rows    = []
mp_feh  = []
mp_afe  = []
mp_dist = []
mp_bprp = []
mp_dorb = []
mp_X    = []
mp_Y    = []
mp_Z    = []

seen_source = set()   # dedup for per-unique-source tables
seen_assoc  = set()   # dedup for (source, stream) pairs

for row in data:
    sid         = int(row["source_id"])
    source_name = f"Gaia DR3 {sid}"
    ref         = first_ref(row["reference"])
    ref2        = second_ref(row["reference"])   # None for single-ref rows
    stream      = str(row["name"]).strip()

    # ── Associations: all 80,162 rows; every (source, stream) pair is unique ──
    assoc_key = (source_name, stream)
    if assoc_key not in seen_assoc:
        seen_assoc.add(assoc_key)
        assoc_rows.append({
            "source":                source_name,
            "association":           stream,
            "membership_probability": f(row["p_mem"]),
            "adopted":               True,
            "comments":              f"ref2: {ref2}" if ref2 else None,
            "reference":             ref,
        })

    # ── Per-unique-source tables ───────────────────────────────────────────────
    if sid in seen_source:
        continue
    seen_source.add(sid)

    plx   = f(row["parallax"])
    pmra_ = f(row["pmra"])
    vr    = f(row["Vr"])
    vr_e  = f(row["Vr_err"])
    if vr_e == 0.0:   # Vr_err==0 means no error reported; store as None
        vr_e = None

    # Parallaxes — skip 5 rows where parallax is NaN
    if plx is not None:
        parallax_rows.append({
            "source":         source_name,
            "parallax_mas":   plx,
            "parallax_error": f(row["parallax_error"]),
            "adopted":        True,
            "comments":       f"ref2: {ref2}" if ref2 else None,
            "reference":      ref,
        })

    # ProperMotions — same 5 NaN rows excluded
    if pmra_ is not None:
        pm_rows.append({
            "source":          source_name,
            "pm_ra":           pmra_,
            "pm_ra_error":     f(row["pmra_error"]),
            "pm_dec":          float(row["pmdec"]),
            "pm_dec_error":    f(row["pmdec_error"]),
            "pmra_pmdec_corr": f(row["pmra_pmdec_corr"]),
            "adopted":         True,
            "comments":        f"ref2: {ref2}" if ref2 else None,
            "reference":       ref,
        })

    # RadialVelocities — skip rows with NaN Vr
    if vr is not None:
        rv_rows.append({
            "source":   source_name,
            "rv_kms":   vr,
            "rv_error": vr_e,
            "adopted":  True,
            "comments": f"ref2: {ref2}" if ref2 else None,
            "reference": ref,
        })

    # Photometry — all unique sources (G-band only)
    phot_rows.append({
        "source":    source_name,
        "band":      "Gaia/Gaia3.G",
        "magnitude": float(row["phot_g_mean_mag"]),
        "telescope": "Gaia",
        "adopted":   True,
        "comments":  f"ref2: {ref2}" if ref2 else None,
        "reference": ref,
        "regime":    "optical",
    })

    # ModeledParameters
    feh_v = f(row["FeH"])
    if feh_v is not None:
        mp_feh.append({"source": source_name, "parameter": "FeH",
                       "value": feh_v, "error": f(row["FeH_err"]),
                       "unit": "dex", "adopted": True,
                       "comments": f"ref2: {ref2}" if ref2 else None,
                       "reference": ref})

    afe_v = f(row["aFe"])
    if afe_v is not None:
        mp_afe.append({"source": source_name, "parameter": "aFe",
                       "value": afe_v, "error": f(row["aFe_err"]),
                       "unit": "dex", "adopted": True,
                       "comments": f"ref2: {ref2}" if ref2 else None,
                       "reference": ref})

    dist_v = f(row["dist"])
    if dist_v is not None:
        mp_dist.append({"source": source_name, "parameter": "dist_kpc",
                        "value": dist_v, "error": f(row["dist_err"]),
                        "unit": "kpc", "adopted": True,
                        "comments": f"ref2: {ref2}" if ref2 else None,
                        "reference": ref})

    mp_bprp.append({"source": source_name, "parameter": "bp_rp",
                    "value": float(row["bp_rp"]), "unit": "mag",
                    "adopted": True,
                    "comments": f"ref2: {ref2}" if ref2 else None,
                    "reference": ref})
    mp_dorb.append({"source": source_name, "parameter": "d_orb_kpc",
                    "value": float(row["d_orb"]), "unit": "kpc",
                    "adopted": True,
                    "comments": f"ref2: {ref2}" if ref2 else None,
                    "reference": ref})
    mp_X.append({"source": source_name, "parameter": "X_kpc",
                 "value": float(row["X"]), "unit": "kpc",
                 "adopted": True,
                 "comments": f"ref2: {ref2}" if ref2 else None,
                 "reference": ref})
    mp_Y.append({"source": source_name, "parameter": "Y_kpc",
                 "value": float(row["Y"]), "unit": "kpc",
                 "adopted": True,
                 "comments": f"ref2: {ref2}" if ref2 else None,
                 "reference": ref})
    mp_Z.append({"source": source_name, "parameter": "Z_kpc",
                 "value": float(row["Z"]), "unit": "kpc",
                 "adopted": True,
                 "comments": f"ref2: {ref2}" if ref2 else None,
                 "reference": ref})

mp_rows_all = mp_bprp + mp_dorb + mp_X + mp_Y + mp_Z + mp_dist + mp_feh + mp_afe

logger.info(
    f"Records built — "
    f"Parallaxes: {len(parallax_rows)}, "
    f"ProperMotions: {len(pm_rows)}, "
    f"RadialVelocities: {len(rv_rows)}, "
    f"Photometry: {len(phot_rows)}, "
    f"Associations: {len(assoc_rows)}, "
    f"ModeledParameters: {len(mp_rows_all)} "
    f"(bp_rp:{len(mp_bprp)}, d_orb:{len(mp_dorb)}, X:{len(mp_X)}, Y:{len(mp_Y)}, "
    f"Z:{len(mp_Z)}, dist:{len(mp_dist)}, FeH:{len(mp_feh)}, aFe:{len(mp_afe)})"
)


def bulk_insert(table, records, label):
    if not records:
        logger.info(f"  {label}: 0 records, skipping")
        return
    with db.session as session:
        session.execute(sa_insert(table), records)
        session.commit()
    logger.info(f"  {label}: {len(records)} rows inserted")


logger.info("Inserting data tables...")
bulk_insert(parallaxes_tbl, parallax_rows, "Parallaxes")
bulk_insert(pm_tbl,         pm_rows,       "ProperMotions")
bulk_insert(rv_tbl,         rv_rows,       "RadialVelocities")
bulk_insert(phot_tbl,       phot_rows,     "Photometry")
bulk_insert(assoc_tbl,      assoc_rows,    "Associations")
bulk_insert(modeled_tbl,    mp_rows_all,   "ModeledParameters")

logger.info("All tables inserted.")

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved to data/")
else:
    logger.info(
        "Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files."
    )
