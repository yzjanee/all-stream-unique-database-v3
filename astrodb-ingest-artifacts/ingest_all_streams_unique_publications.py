"""
Ingest 15 publications from all_streams_unique.fits into the Publications table.

DOIs and bibcodes were resolved in v2 (all-stream-unique-database-v2) and carried forward.
No ADS token needed — all metadata is supplied explicitly via ignore_ads=True.

Run:
    python3 astrodb-ingest-artifacts/ingest_all_streams_unique_publications.py

Set SAVE_DB = True to write changes to data/reference/Publications.json.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astrodb_utils import build_db_from_json
from astrodb_utils.publications import ingest_publication, find_publication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_FILE = "database.toml"
SAVE_DB = True  # Set to True after successful dry run to persist changes

PUBLICATIONS = [
    {
        "reference": "Awad2024",
        "doi": "10.1051/0004-6361/202347848",
        "bibcode": "2024A&A...683A..14A",
        "description": "Swarming in stellar streams: Unveiling the structure of the Jhelum stream with ant colony-inspired computation",
    },
    {
        "reference": "Bona20",
        "doi": "10.3847/2041-8213/ab800c",
        "bibcode": "2020ApJ...892L..37B",
        "description": "High-resolution Spectroscopy of the GD-1 Stellar Stream Localizes the Perturber near the Orbital Plane of Sagittarius",
    },
    {
        "reference": "Chan22",
        "doi": "10.3847/1538-4357/ac9b4b",
        "bibcode": "2022ApJ...940..127C",
        "description": "A Ghost in Boötes: The Least-Luminous Disrupted Dwarf Galaxy",
    },
    {
        "reference": "Ferg22",
        "doi": "10.3847/1538-3881/ac3492",
        "bibcode": "2022AJ....163...18F",
        "description": "DELVE-ing into the Jet: A Thin Stellar Stream on a Retrograde Orbit at 30 kpc",
    },
    {
        "reference": "Gril19",
        "doi": "10.3847/1538-4357/ab441d",
        "bibcode": "2019ApJ...884..174G",
        "description": "Detection of a 50° long Trailing Tidal Tail for the Globular Cluster M5",
    },
    {
        "reference": "Gril22",
        "doi": "10.3847/1538-4357/ac5bd7",
        "bibcode": "2022ApJ...929...89G",
        "description": "The Extended Tidal Tails of NGC 7089 (M2)",
    },
    {
        "reference": "Huan19",
        "doi": "10.3847/1538-4357/ab158a",
        "bibcode": "2019ApJ...877...13H",
        "description": "Member Stars of the GD-1 Tidal Stream from the SDSS, LAMOST, and Gaia Surveys",
    },
    {
        "reference": "Ibat24",
        "doi": "10.3847/1538-4357/ad382d",
        "bibcode": "2024ApJ...967...89I",
        "description": "Charting the Galactic Acceleration Field. II. A Global Mass Model of the Milky Way from the STREAMFINDER Atlas of Stellar Streams Detected in Gaia DR3",
    },
    {
        "reference": "Kopo23",
        "doi": "10.1093/mnras/stad551",
        "bibcode": "2023MNRAS.521.4936K",
        "description": "S5: Probing the Milky Way and Magellanic Clouds potentials with the 6D map of the Orphan-Chenab stream",
    },
    {
        "reference": "Li__21",
        "doi": "10.3847/1538-4357/abeb18",
        "bibcode": "2021ApJ...911..149L",
        "description": "Broken into Pieces: ATLAS and Aliqa Uma as One Single Stream",
    },
    {
        "reference": "Ship19",
        "doi": "10.3847/1538-4357/ab44bf",
        "bibcode": "2019ApJ...885....3S",
        "description": "Proper Motions of Stellar Streams Discovered in the Dark Energy Survey",
    },
    {
        "reference": "Ship20",
        "doi": "10.3847/1538-3881/abbd3a",
        "bibcode": "2020AJ....160..244S",
        "description": "Discovery of Extended Tidal Tails around the Globular Cluster Palomar 13",
    },
    {
        "reference": "Vasi21",
        "doi": "10.1093/mnras/staa3673",
        "bibcode": "2021MNRAS.501.2279V",
        "description": "Tango for three: Sagittarius, LMC, and the Milky Way",
    },
    {
        "reference": "Yang22",
        "doi": "10.1051/0004-6361/202243976",
        "bibcode": "2022A&A...667A..37Y",
        "description": "Existence of tidal tails for the globular cluster NGC 5824",
    },
    {
        "reference": "Yang23",
        "doi": "10.3847/1538-4357/acdee2",
        "bibcode": "2023ApJ...953..130Y",
        "description": "The Spectacular Tidal Tails of Globular Cluster M3 (NGC 5272)",
    },
]

db = build_db_from_json(settings_file=SETTINGS_FILE)

added = 0
already_present = 0
failed = 0

for pub in PUBLICATIONS:
    ref = pub["reference"]
    doi = pub["doi"]

    found, _ = find_publication(db, doi=doi)
    if found:
        logger.info(f"Already present: {ref} (doi={doi})")
        already_present += 1
        continue

    try:
        ingest_publication(
            db,
            reference=ref,
            doi=doi,
            bibcode=pub["bibcode"],
            description=pub["description"],
            ignore_ads=True,
        )
        logger.info(f"Added: {ref}")
        added += 1
    except Exception as e:
        logger.error(f"Failed: {ref} — {e}")
        failed += 1

logger.info(f"\nSummary: {added} added, {already_present} already present, {failed} failed")

if SAVE_DB:
    db.save_database("data/")
    logger.info("Database saved to data/")
else:
    logger.info("Dry run complete — NOT saved. Set SAVE_DB = True to write the database to JSON files.")
