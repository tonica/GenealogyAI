"""Tests del parser GEDCOM (sense persistència)."""

import pytest

from app.importer import GedcomParseError, parse, read_lines

SAMPLE = """0 HEAD
1 SOUR GenealogyAI
1 GEDC
2 VERS 5.5.5
1 DATE 1 JAN 2000
0 @I1@ INDI
1 NAME Juan /Garcia/
1 SEX M
1 BIRT
2 DATE 10 FEB 1890
2 PLAC Barcelona
1 DEAT
2 DATE 3 MAY 1970
0 @I2@ INDI
1 NAME Maria /Perez/
1 SEX F
1 BIRT
2 DATE 15 JUN 1892
2 PLAC Madrid
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I1@
0 TRLR
"""


def test_read_lines_normatatag_tokens():
    lines = read_lines(SAMPLE)
    tags = [line.tag for line in lines]
    assert "INDI" in tags
    assert "HUSB" in tags
    assert any(line.tag == "HEAD" for line in lines)


def test_parse_person_names_and_sex():
    doc = parse(SAMPLE)
    juan = doc.person_by_xref("I1")
    assert juan is not None
    assert juan.xref == "I1"
    assert juan.names[0].given == "Juan"
    assert juan.names[0].surname == "Garcia"
    assert juan.sex == "M"


def test_parse_birth_event():
    doc = parse(SAMPLE)
    juan = doc.person_by_xref("I1")
    birth = juan.birth
    assert birth is not None
    assert birth.type == "birth"
    assert birth.date == "10 FEB 1890"
    assert birth.place == "Barcelona"


def test_parse_death_and_event_of():
    doc = parse(SAMPLE)
    juan = doc.persons[0]
    assert juan.death.type == "death"
    assert juan.death.date == "3 MAY 1970"


def test_parse_family_parts():
    doc = parse(SAMPLE)
    fam = doc.families[0]
    assert fam.xref == "F1"
    assert fam.husband == "I1"
    assert fam.wife == "I2"
    assert "I1" in fam.children


def test_name_with_prefix_and_suffix():
    text = "0 @I9@ INDI\n1 NAME Don /Garcia/ Juan\n1 SEX M\n0 TRLR"
    n = parse(text).persons[0].names[0]
    assert n.given == "Don"
    assert n.surname == "Garcia"
    assert n.suffix == "Juan"


def test_name_surname_only():
    text = "0 @I1@ INDI\n1 NAME /Garcia/\n0 TRLR"
    n = parse(text).persons[0].names[0]
    assert n.given == ""
    assert n.surname == "Garcia"


def test_events_capture_sources_and_notes():
    text = (
        "0 @I1@ INDI\n"
        "1 NAME A /B/\n"
        "1 BIRT\n"
        "2 PLAC Paris\n"
        "2 SOUR @S1@\n"
        "2 NOTE una mica de text\n"
        "0 @S1@ SOUR\n"
        "1 TITL Registre Civil\n"
        "1 AUTH Ajuntament\n"
    )
    doc = parse(text)
    p = doc.persons[0]
    birth = p.birth
    assert birth.place == "Paris"
    assert birth.sources == ["S1"]
    assert birth.notes == ["una mica de text"]
    assert doc.sources["S1"].title == "Registre Civil"
    assert doc.sources["S1"].author == "Ajuntament"


def test_continuation_conc_and_cont():
    # CONC sense espai inicial es concatenat literalment;
    # un espai doble (un dels quals toca al tag) preserva un espai inicial.
    text = (
        "0 @N1@ NOTE Primera linia\n"
        "1 CONC i segona\n"
        "1 CONC  amb espai\n"
        "1 CONT tercera linia\n"
        "0 @I1@ INDI\n"
        "1 NAME A /B/\n"
        "1 NOTE @N1@\n"
    )
    doc = parse(text)
    assert doc.notes["N1"].text == "Primera liniai segona amb espai\ntercera linia"
    assert doc.persons[0].note_refs == ["N1"]


def test_source_record_parsing():
    text = (
        "0 @S5@ SOUR\n"
        "1 TITL Llibre dels difunts\n"
        "1 AUTH J. Perez\n"
        "1 PUBL Madrid 1900\n"
        "1 PAGE p.123\n"
    )
    src = parse(text).sources["S5"]
    assert src.title == "Llibre dels difunts"
    assert src.author == "J. Perez"
    assert src.publication == "Madrid 1900"
    assert src.page == "p.123"


def test_media_record():
    text = "0 @O1@ OBJE\n1 FILE /imatge/foto.jpg\n1 TITL Boda\n"
    doc = parse(text)
    assert doc.media["O1"].file == "/imatge/foto.jpg"
    assert doc.media["O1"].title == "Boda"


def test_person_links_to_media_source_note():
    text = (
        "0 @I1@ INDI\n"
        "1 NAME A /B/\n"
        "1 NOTE una notreta\n"
        "1 SOUR @S1@\n"
        "1 OBJE @O1@\n"
    )
    p = parse(text).persons[0]
    assert p.note_texts == ["una notreta"]
    assert p.sources == ["S1"]
    assert p.media == ["O1"]


def test_parse_marriage_and_divorce_in_family():
    text = (
        "0 @F7@ FAM\n"
        "1 HUSB @I1@\n"
        "1 WIFE @I2@\n"
        "1 MARR\n"
        "2 DATE 5 JUL 1910\n"
        "2 PLAC Sevilla\n"
        "1 DIV\n"
        "2 DATE 2 JAN 1920\n"
    )
    fam = parse(text).families[0]
    marr = fam.event_of("marriage")
    assert marr.date == "5 JUL 1910"
    assert marr.place == "Sevilla"
    assert fam.event_of("divorce").date == "2 JAN 1920"


def test_invalid_line_raises():
    with pytest.raises(GedcomParseError):
        parse("AQUESTA LINIA NO TE NIVELL")


def test_parse_file_path(tmp_path):
    f = tmp_path / "arbre.ged"
    f.write_text(SAMPLE, encoding="utf-8")
    doc = parse(f)
    assert doc.person_by_xref("I1") is not None
    assert len(doc.families) == 1


def test_family_as_parent_links():
    text = "0 @I1@ INDI\n1 NAME A /B/\n1 FAMS @F1@\n1 FAMC @F2@\n"
    p = parse(text).persons[0]
    assert p.families_as_spouse == ["F1"]
    assert p.families_as_child == ["F2"]


def test_parse_strips_utf8_bom_on_first_line():
    # Els fitxers reals (ex. export MyHeritage) comencen amb un BOM UTF-8
    # \ufeff que no es pot quedar enganxat al nivell de la primera línia.
    text = "\ufeff" + "0 @I1@ INDI\n1 NAME A /B/\n0 TRLR\n"
    doc = parse(text)
    assert len(doc.persons) == 1
    assert doc.persons[0].xref == "I1"


def test_parse_file_with_bom_and_crlf(tmp_path):
    # BOM + CRLF (CRLF realistes des d'un exportador a Windows).
    raw = "\ufeff0 @I1@ INDI\r\n1 NAME A /B/\r\n0 TRLR\r\n"
    f = tmp_path / "arbre.ged"
    f.write_bytes(raw.encode("utf-8"))
    doc = parse(f)
    assert len(doc.persons) == 1
