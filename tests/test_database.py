"""
Tests that the database ORM layer functions work as expected.
"""

from sqlalchemy.ext.automap import automap_base


def test_orm_use(db):
    Base = automap_base(metadata=db.metadata)
    Base.prepare()

    Sources = Base.classes.Sources
    Names = Base.classes.Names
    Publications = Base.classes.Publications

    # Add a test publication first (Sources.reference has an FK to Publications)
    ref = Publications(reference="Test00")
    s = Sources(source="Test Source", ra_deg=10.0, dec_deg=-20.0,
                epoch_year=2016.0, reference="Test00")
    n = Names(source="Test Source", other_name="TS-001")

    with db.session as session:
        session.add(ref)
        session.add(s)
        session.add(n)
        session.commit()

    assert db.query(db.Sources).filter(db.Sources.c.source == "Test Source").count() == 1
    assert db.query(db.Names).filter(db.Names.c.other_name == "TS-001").count() == 1

    with db.session as session:
        session.delete(n)
        session.delete(s)
        session.delete(ref)
        session.commit()

    assert db.query(db.Sources).filter(db.Sources.c.source == "Test Source").count() == 0


def test_adding_data(db):
    assert db.query(db.Sources).filter(db.Sources.c.source == "Test Source 2").count() == 0

    Base = automap_base(metadata=db.metadata)
    Base.prepare()

    Sources = Base.classes.Sources
    Publications = Base.classes.Publications
    Telescopes = Base.classes.Telescopes
    Photometry = Base.classes.Photometry
    PhotometryFilters = Base.classes.PhotometryFilters
    RegimeList = Base.classes.RegimeList

    ref = Publications(reference="Test01")
    s = Sources(source="Test Source 2", ra_deg=20.0, dec_deg=-30.0,
                epoch_year=2016.0, reference="Test01")
    tel = Telescopes(telescope="TestTel", reference="Test01")
    pf = PhotometryFilters(band="TestBand", effective_wavelength_angstroms=6231.0)
    reg = RegimeList(regime="test_optical")

    with db.session as session:
        session.add_all([ref, pf, tel, s, reg])
        session.commit()

    assert db.query(db.Sources).filter(db.Sources.c.source == "Test Source 2").count() == 1

    phot = Photometry(
        source="Test Source 2",
        band="TestBand",
        magnitude=15.0,
        telescope="TestTel",
        reference="Test01",
        regime="test_optical",
    )
    with db.session as session:
        session.add(phot)
        session.commit()

    assert db.query(db.Photometry).filter(db.Photometry.c.source == "Test Source 2").count() == 1

    with db.session as session:
        session.delete(phot)
        session.commit()
    with db.session as session:
        session.delete(s)
        session.delete(ref)
        session.delete(tel)
        session.delete(pf)
        session.delete(reg)
        session.commit()
