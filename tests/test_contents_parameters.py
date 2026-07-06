"""
Tests for ModeledParameters table.
Update expected counts as data is ingested.
"""

from astropy import units as u


def test_modeled_parameters(db):
    n = db.query(db.ModeledParameters.c.parameter).count()
    # Expected after ingestion: ~458,000 rows across 8 parameters
    # (bp_rp, d_orb_kpc, X_kpc, Y_kpc, Z_kpc, dist_kpc, FeH, aFe)
    assert n == 0, f"Found {n} ModeledParameters rows (expected 0 before ingestion)"

    # All units must be astropy-resolvable
    t = (
        db.query(db.ModeledParameters)
        .filter(db.ModeledParameters.c.unit.isnot(None))
        .distinct()
        .astropy()
    )
    unit_fail = []
    for x in t:
        unit = x["unit"]
        try:
            assert u.Unit(unit, parse_strict="raise")
        except ValueError:
            counts = db.query(db.ModeledParameters).filter(
                db.ModeledParameters.c.unit == unit
            ).count()
            unit_fail.append({unit: counts})

    assert len(unit_fail) == 0, f"Some parameter units did not resolve: {unit_fail}"


def test_associations(db):
    n = db.query(db.Associations.c.source).count()
    # Expected after ingestion: 80,162 rows (includes both memberships for 27 duplicate stars)
    assert n == 0, f"Found {n} Associations rows (expected 0 before ingestion)"
