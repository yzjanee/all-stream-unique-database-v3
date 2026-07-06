"""
Tests for kinematic and astrometric tables: Parallaxes, ProperMotions, RadialVelocities.
Update expected counts as data is ingested.
"""

from sqlalchemy import func


def test_parallaxes(db):
    n = db.query(db.Parallaxes.c.parallax_mas).count()
    # 80,130 = 80,135 unique sources minus 5 with NaN parallax
    assert n == 80130, f"Found {n} parallaxes (expected 80130)"

    # Every source with a parallax should have exactly one adopted = True
    t = (
        db.query(
            db.Parallaxes.c.source,
            func.sum(db.Parallaxes.c.adopted).label("adopted_counts"),
        )
        .group_by(db.Parallaxes.c.source)
        .having(func.sum(db.Parallaxes.c.adopted) != 1)
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} sources have incorrect adopted count in Parallaxes"


def test_proper_motions(db):
    n = db.query(db.ProperMotions.c.pm_ra).count()
    # 80,130 = same 5 NaN sources excluded
    assert n == 80130, f"Found {n} proper motion rows (expected 80130)"

    # Every source with a ProperMotion should have exactly one adopted = True
    t = (
        db.query(
            db.ProperMotions.c.source,
            func.sum(db.ProperMotions.c.adopted).label("adopted_counts"),
        )
        .group_by(db.ProperMotions.c.source)
        .having(func.sum(db.ProperMotions.c.adopted) != 1)
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} sources have incorrect adopted count in ProperMotions"


def test_radial_velocities(db):
    n = db.query(db.RadialVelocities.c.rv_kms).count()
    # 6,942 sources with non-NaN Vr (73,193 excluded)
    assert n == 6942, f"Found {n} radial velocity rows (expected 6942)"

    t = (
        db.query(
            db.RadialVelocities.c.source,
            func.sum(db.RadialVelocities.c.adopted).label("adopted_counts"),
        )
        .group_by(db.RadialVelocities.c.source)
        .having(func.sum(db.RadialVelocities.c.adopted) != 1)
        .astropy()
    )
    assert len(t) == 0, f"{len(t)} sources have incorrect adopted count in RadialVelocities"
