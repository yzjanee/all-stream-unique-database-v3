"""
Tests for the database contents.
Update expected counts as data is ingested.
"""

from sqlalchemy import or_


def test_table_presence(db):
    assert len(db.metadata.tables.keys()) == 15
    # Lookup tables
    assert "Publications" in db.metadata.tables.keys()
    assert "Telescopes" in db.metadata.tables.keys()
    assert "Instruments" in db.metadata.tables.keys()
    assert "PhotometryFilters" in db.metadata.tables.keys()
    assert "RegimeList" in db.metadata.tables.keys()
    assert "AssociationList" in db.metadata.tables.keys()
    assert "ParameterList" in db.metadata.tables.keys()
    # Main tables
    assert "Sources" in db.metadata.tables.keys()
    assert "Names" in db.metadata.tables.keys()
    # Data tables
    assert "Photometry" in db.metadata.tables.keys()
    assert "Parallaxes" in db.metadata.tables.keys()
    assert "ProperMotions" in db.metadata.tables.keys()
    assert "RadialVelocities" in db.metadata.tables.keys()
    assert "Associations" in db.metadata.tables.keys()
    assert "ModeledParameters" in db.metadata.tables.keys()


def test_magnitudes(db):
    t = (
        db.query(db.Photometry.c.magnitude)
        .filter(
            or_(
                db.Photometry.c.magnitude > 100,
                db.Photometry.c.magnitude < -1,
            )
        )
        .astropy()
    )

    assert len(t) == 0, f"{len(t)} Photometry failed magnitude checks"
