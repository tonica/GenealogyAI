"""Tests del importador a la base de dades."""

from app.importer import parse
from app.models import Event, Person, Place, Source
from app.services.importer import import_gedcom

GED = """0 HEAD
0 @I1@ INDI
1 NAME John /Garcia/
1 SEX M
1 BIRT
2 DATE 10 FEB 1890
2 PLAC barcelona
1 DEAT
2 DATE 28 FEB 1970
0 @I2@ INDI
1 NAME maria /PEREZ/
1 SEX F
1 BIRT
2 DATE 3 JUN 1895
2 PLAC Madrid
1 SOUR @S1@
1 OBJE @O1@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 MARR
2 DATE 5 JUL 1910
2 PLAC sevilla
0 @S1@ SOUR
1 TITL Registre Civil
0 @O1@ OBJE
1 FILE /fotos/a.jpg
0 TRLR
"""


def test_import_persists_basic_counts(test_session):
    doc = parse(GED)
    res = import_gedcom(test_session, doc)

    persona = test_session.query(Person).count()
    assert persona == 2
    assert test_session.query(Event).count() >= 3
    assert res.families == 1


def test_import_normalizes_names_and_surnames(test_session):
    doc = parse(GED)
    import_gedcom(test_session, doc)
    juan = test_session.query(Person).filter_by(xref="I1").one()
    assert juan.given_name == "John"
    assert juan.surname == "Garcia"
    maria = test_session.query(Person).filter_by(xref="I2").one()
    assert maria.surname == "Perez"


def test_import_normalizes_dates(test_session):
    doc = parse(GED)
    import_gedcom(test_session, doc)
    ev = test_session.query(Event).filter_by(event_type="birth").first()
    assert ev.date_year == 1890
    assert ev.date_iso == "1890-02-10"


def test_import_dedupe_places_by_normalized_key(test_session):
    # Mateix nom amb accent/injection -> una sola fila a `places`.
    text = (
        "0 @I1@ INDI\n1 NAME A /B/\n1 BIRT\n2 PLAC barcelona\n"
        "0 @I2@ INDI\n1 NAME C /D/\n1 BIRT\n2 PLAC Barcelona\n"
    )
    import_gedcom(test_session, parse(text))

    assert test_session.query(Place).count() == 1


def test_import_links_source_and_media(test_session):
    doc = parse(GED)
    import_gedcom(test_session, doc)
    maria = test_session.query(Person).filter_by(xref="I2").one()
    assert [s.xref for s in maria.sources] == ["S1"]
    assert [m.xref for m in maria.media] == ["O1"]
    assert test_session.query(Source).count() == 1


def test_import_detects_missing_references(test_session):
    text = "0 @I1@ INDI\n1 NAME A /B/\n1 SOUR @S99@\n"
    res = import_gedcom(test_session, parse(text))
    codes = [i.code for i in res.issues]
    assert "missing_source" in codes


def test_import_generates_stats(test_session):
    doc = parse(GED)
    res = import_gedcom(test_session, doc)
    stats = res.stats.to_dict()
    assert stats["persons"] == 2
    assert stats["families"] == 1
    assert stats["events_by_type"]["birth"] == 2
    assert stats["sex_by"]["M"] == 1
    assert stats["sex_by"]["F"] == 1


def test_import_dedupes_sources_by_title(test_session):
    # La DB obliga `sources.title` únic; MyHeritage pot exportar dos SOUR
    # amb el mateix títol (xrefs S1 i S2). Han d'apuntar a una sola fila.
    text = (
        "0 @S1@ SOUR\n1 TITL Web Site\n"
        "0 @S2@ SOUR\n1 TITL Web Site\n"
        "0 @I1@ INDI\n1 NAME A /B/\n1 SOUR @S1@\n1 SOUR @S2@\n"
    )
    res = import_gedcom(test_session, parse(text))
    assert res.sources == 2
    assert test_session.query(Source).count() == 1
    person = test_session.query(Person).filter_by(xref="I1").one()
    assert len(person.sources) == 1


def test_import_given_untitled_sources_different_rows(test_session):
    """Dos SOUR amb títols diferents -> dues files, sense col·lisió."""
    text = (
        "0 @S1@ SOUR\n1 TITL Registre Civil\n" "0 @S2@ SOUR\n1 TITL Llibre parroquial\n"
    )
    import_gedcom(test_session, parse(text))
    assert test_session.query(Source).count() == 2
