"""
Ingest 80,135 unique Gaia DR3 stream members into Sources + Names.

Source naming: "Gaia DR3 <source_id>"  (primary key in Sources)
Alternate name: "<source_id>" raw integer string added to Names.
epoch_year = 2016.0 for all sources (Gaia DR3 reference epoch J2016.0).

27 source_ids appear twice (stars in two overlapping streams per Ibata2024).
These are deduplicated: first occurrence wins for Sources; both stream memberships
are handled when Associations is ingested later.

SESAME/SIMBAD check (astrodb-ingest-sources Step 1.5): skipped.
Source names are systematic Gaia DR3 IDs — 80k SIMBAD queries would take
hours, and most stream candidates are not individually catalogued.

The FITS file stores full author names (e.g. "Bonaca2020") while our Publications
table uses 4+2 shortnames (e.g. "Bona20"). REFERENCE_MAP translates between them.

Run with SAVE_DB = False for dry run, then True on explicit confirmation.
"""

import logging
import numpy as np
from astropy.table import Table
from sqlalchemy.exc import IntegrityError

from astrodb_utils import build_db_from_json
from astrodb_utils.sources import ingest_source
from sqlalchemy.ext.automap import automap_base

logging.getLogger("astrodb_utils").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s - %(message)s")

SAVE_DB = False  # Set to True after successful dry run to persist changes

SETTINGS_FILE = "database.toml"
TABLE_PATH = "../all-stream-unique-database-v2/all_streams_unique.fits"

# DB schema column names (astrodb-template-db defaults)
RA_COL_NAME    = "ra_deg"
DEC_COL_NAME   = "dec_deg"
EPOCH_COL_NAME = "epoch_year"

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

# ── Load data ──────────────────────────────────────────────────────────────────
data = Table.read(TABLE_PATH, format="fits")
logger.info(f"Loaded {len(data)} rows from {TABLE_PATH}")

db = build_db_from_json(settings_file=SETTINGS_FILE)

Base = automap_base(metadata=db.metadata)
Base.prepare()
Names = Base.classes.Names

# ── Ingest loop ────────────────────────────────────────────────────────────────
seen_source_ids = set()
sources_added = sources_skipped = names_added = 0

for row in data:
    source_id = int(row["source_id"])

    # Deduplicate: 27 stars appear in two streams; only one Sources row per star
    if source_id in seen_source_ids:
        logger.debug(f"Duplicate source_id {source_id} — skipping Sources row")
        continue
    seen_source_ids.add(source_id)

    source_name = f"Gaia DR3 {source_id}"

    # Extract first reference from comma-separated list and map to shortname
    raw_ref = str(row["reference"]).strip().split(",")[0].strip()
    reference = REFERENCE_MAP.get(raw_ref)
    if reference is None:
        logger.warning(f"Unknown reference '{raw_ref}' for {source_name} — skipping")
        sources_skipped += 1
        continue

    ra  = float(row["ra"])
    dec = float(row["dec"])

    try:
        ingest_source(
            db,
            source=source_name,
            reference=reference,
            ra=ra,
            dec=dec,
            epoch="2016.0",
            ra_col_name=RA_COL_NAME,
            dec_col_name=DEC_COL_NAME,
            epoch_col_name=EPOCH_COL_NAME,
            use_simbad=False,
            raise_error=True,
            search_db=False,  # dedup handled by seen_source_ids; search_db=True triggers
                              # astrodbkit query_region which fails on empty DataFrames
        )
        sources_added += 1

        # Add raw Gaia source_id integer as alternate name in Names
        try:
            with db.session as session:
                session.add(Names(source=source_name, other_name=str(source_id)))
                session.commit()
            names_added += 1
        except IntegrityError:
            pass  # already present (shouldn't happen on a fresh DB)

    except Exception as e:
        sources_skipped += 1
        logger.warning(f"Skipping {source_name}: {e}")

logger.info(
    f"\nDone: {sources_added} sources ingested, {names_added} alternate names added, "
    f"{sources_skipped} skipped out of {len(seen_source_ids)} unique source_ids "
    f"({len(data)} total rows)"
)

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved to data/")
else:
    logger.info(
        "Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files."
    )
