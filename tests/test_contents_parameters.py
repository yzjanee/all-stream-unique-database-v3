"""
Tests for ModeledParameters table.
Update expected counts as data is ingested.
"""

from astropy import units as u


def test_modeled_parameters(db):
    n = db.query(db.ModeledParameters.c.parameter).count()
    # 458,088 rows across 8 parameters (bp_rp, d_orb_kpc, X_kpc, Y_kpc, Z_kpc,
    # dist_kpc=55,397, FeH=1,967, aFe=49; rest have all 80,135 unique sources)
    assert n == 458088, f"Found {n} ModeledParameters rows (expected 458088)"

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
    # 80,162 rows: all (source, stream) pairs including both memberships for 27 duplicate stars
    assert n == 80162, f"Found {n} Associations rows (expected 80162)"
