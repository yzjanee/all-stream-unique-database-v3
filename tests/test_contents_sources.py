"""
Tests for the Sources and Names tables.
Update expected counts as data is ingested.
"""

from sqlalchemy import or_


def test_sources(db):
    n_sources = db.query(db.Sources).count()
    # 80,135 unique Gaia DR3 sources (80,162 rows minus 27 duplicate source_ids)
    assert n_sources == 80135, f"found {n_sources} sources (expected 80135)"


def test_names(db):
    n_names = db.query(db.Names).count()
    # 160,270 names: 2 per source ("Gaia DR3 <id>" primary + raw integer alternate)
    assert n_names == 160270, f"found {n_names} names (expected 160270)"


def test_coordinates(db):
    t = (
        db.query(db.Sources.c.source, db.Sources.c.ra_deg, db.Sources.c.dec_deg)
        .filter(
            or_(
                db.Sources.c.ra_deg.is_(None),
                db.Sources.c.ra_deg < 0,
                db.Sources.c.ra_deg > 360,
                db.Sources.c.dec_deg.is_(None),
                db.Sources.c.dec_deg < -90,
                db.Sources.c.dec_deg > 90,
            )
        )
        .astropy()
    )

    assert len(t) == 0, f"{len(t)} Sources failed coordinate checks: {t}"


def test_epoch_year(db):
    # After ingestion, all sources should have epoch_year = 2016.0 (Gaia DR3)
    t = (
        db.query(db.Sources.c.source)
        .filter(
            db.Sources.c.ra_deg.isnot(None),
            db.Sources.c.epoch_year.is_(None),
        )
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} Sources with coordinates but no epoch_year"
