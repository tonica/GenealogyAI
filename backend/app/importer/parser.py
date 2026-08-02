"""Parser de GEDCOM 5.5.1 escrit des de zero (sense llibreries externes).

Flux:
  1. Llegir el text a línies i normalitzar-les a `RawLine` (nivell, tag, valor).
  2. Construir un arbre de `RawRecord` (línies anidades segons el nivell).
  3. Convertir l'arbre en els objectes neutrals de `app.importer.models`.

La tokenització, la construcció de l'arbre i la conversió a objectes estan
separades per poder provar cada etapa de manera aïllada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.importer.models import (
    Event,
    Family,
    GedcomDocument,
    MediaRecord,
    Name,
    NoteRecord,
    Person,
    SourceRecord,
)

# Tags que representen esdeveniments vitals (i el nom canònic de cadascun).
_EVENT_LABELS = {
    "BIRT": "birth",
    "DEAT": "death",
    "MARR": "marriage",
    "DIV": "divorce",
    "BAPM": "baptism",
    "CHR": "christening",
    "BURI": "burial",
    "CENS": "census",
    "EDUC": "education",
    "EMIG": "emigration",
    "GRAD": "graduation",
    "IMMI": "immigration",
    "NATU": "naturalization",
    "OCCU": "occupation",
    "PROB": "probate",
    "RESI": "residence",
    "RETI": "retirement",
    "WILL": "will",
    "ADOP": "adoption",
    "EVEN": "event",
}

EVENT_TAGS = frozenset(_EVENT_LABELS.keys())

# Tags de continuació de la línia anterior.
CONTINUATION_TAGS = frozenset({"CONT", "CONC"})


class GedcomParseError(ValueError):
    """Llança quan el fitxer no és un GEDCOM vàlid."""


@dataclass
class RawLine:
    """Una línia GEDCOM normalitzada.

    `xref` es el identificador de registre (davant del tag) com `@I1@`,
    quan existeix.
    """

    level: int
    tag: str
    value: str
    xref: str = ""


@dataclass
class RawRecord:
    """Un node de l'arbre: una línia i els seus descendents."""

    level: int
    tag: str
    value: str
    xref: str = ""
    children: list["RawRecord"] = field(default_factory=list)

    def child(self, *tags: str) -> "RawRecord | None":
        for c in self.children:
            if c.tag in tags:
                return c
        return None

    def children_of(self, *tags: str) -> list["RawRecord"]:
        return [c for c in self.children if c.tag in tags]


def _strip_xref(value: str) -> str:
    """Elimina les arroves d'un identificador GEDCOM com '@I1@'."""
    return value.strip().strip("@").strip()


def read_lines(source: str | bytes | Path | list[str]) -> list[RawLine]:
    """Normalitza un GEDCOM en línies `RawLine`."""
    if isinstance(source, Path):
        lines = source.read_text(encoding="utf-8", errors="replace").splitlines()
    elif isinstance(source, bytes):
        lines = source.decode("utf-8", errors="replace").splitlines()
    elif isinstance(source, str):
        lines = source.splitlines()
    else:
        lines = source

    tokens: list[RawLine] = []
    for lineno, raw in enumerate(lines, start=1):
        line = raw.lstrip("\ufeff").rstrip("\r\n ")
        if not line.strip():
            continue
        stripped = line.lstrip()
        level_ch = stripped[:1]
        if not level_ch.isdigit():
            raise GedcomParseError(f"Línia {lineno}: nivell no numèric: {line!r}")
        level = int(level_ch)
        rest = stripped[1:].strip()
        if not rest:
            raise GedcomParseError(f"Línia {lineno}: falta el tag: {line!r}")

        xref = ""
        if rest.startswith("@"):
            # Forma apunta: "0 @I1@ INDI" -> identificador abans del tag.
            if " " in rest:
                pointer, remainder = rest.split(" ", 1)
                poke = pointer
                xref = poke.strip("@").strip()
                rest = remainder
            else:
                raise GedcomParseError(f"Línia {lineno}: punter sense tag: {line!r}")

        if " " in rest:
            tag, value = rest.split(" ", 1)
        else:
            tag, value = rest, ""
        tokens.append(RawLine(level=level, tag=tag.upper(), value=value, xref=xref))
    return tokens


def _build_tree(records: list[RawLine]) -> list[RawRecord]:
    """Construeix l'arbre: a cada línia se li assignen els descendents."""
    roots: list[RawRecord] = []
    stack: list[RawRecord] = []
    for rec in records:
        node = RawRecord(level=rec.level, tag=rec.tag, value=rec.value, xref=rec.xref)
        while stack and stack[-1].level >= rec.level:
            stack.pop()
        if stack:
            stack[-1].children.append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def parse(source: str | bytes | Path | list[str]) -> GedcomDocument:
    """Parse una font GEDCOM i retorna un `GedcomDocument`."""
    lines = read_lines(source)
    roots = _build_tree(lines)
    return _convert(roots)


# ------------------------------------------------------------------ conversió


def _event_type(tag: str) -> str:
    return _EVENT_LABELS.get(tag, tag.lower())


def _combined_value(rec: RawRecord) -> str:
    """Valor del node incorporant les continuacions CONT/CONC."""
    parts: list[str] = [rec.value] if rec.value else []
    for c in rec.children_of(*CONTINUATION_TAGS):
        if c.tag == "CONT":
            parts.append("\n" + c.value)
        else:
            parts.append(c.value)
    return "".join(parts)


def _value(rec: RawRecord | None) -> str | None:
    if rec is None:
        return None
    return _combined_value(rec) or None


def _xref_list(rec: RawRecord | None, tag: str) -> list[str]:
    if rec is None:
        return []
    out: list[str] = []
    for c in rec.children_of(tag):
        val = c.value.strip()
        if val.startswith("@"):
            out.append(_strip_xref(val))
    return out


def _note_targets(rec: RawRecord, target: Person | Family) -> None:
    val = rec.value.strip()
    if val.startswith("@"):
        target.note_refs.append(_strip_xref(val))
    else:
        target.note_texts.append(_combined_value(rec))


def _parse_event(rec: RawRecord) -> Event:
    ev = Event(type=_event_type(rec.tag))
    ev.date = _value(rec.child("DATE"))
    ev.place = _value(rec.child("PLAC"))
    ev.notes = [
        c.value for c in rec.children_of("NOTE") if not c.value.strip().startswith("@")
    ]
    ev.sources = _xref_list(rec, "SOUR")
    ev.media = _xref_list(rec, "OBJE")
    return ev


def _parse_name(rec: RawRecord) -> Name:
    value = _combined_value(rec)

    given, surname, suffix = "", "", ""
    first = value.find("/")
    last = value.rfind("/")
    if first != -1 and last != -1 and last >= first:
        given = value[:first].strip()
        surname = value[first + 1 : last].strip()
        suffix = value[last + 1 :].strip()
    else:
        given = value.strip()

    name = Name(value=value, given=given, surname=surname, suffix=suffix)
    givn = rec.child("GIVN")
    surn = rec.child("SURN")
    nick = rec.child("NICK")
    if givn and givn.value:
        name.given = givn.value.strip()
    if surn and surn.value:
        name.surname = surn.value.strip()
    if nick and nick.value:
        name.suffix = nick.value.strip()
    return name


def _parse_person(rec: RawRecord) -> Person:
    p = Person(xref=rec.xref)
    for c in rec.children:
        if c.tag == "NAME":
            p.names.append(_parse_name(c))
        elif c.tag == "SEX" and c.value:
            p.sex = c.value.strip()
        elif c.tag in EVENT_TAGS:
            p.events.append(_parse_event(c))
        elif c.tag == "NOTE":
            _note_targets(c, p)
        elif c.tag == "SOUR":
            if c.value.strip().startswith("@"):
                p.sources.append(_strip_xref(c.value))
        elif c.tag == "OBJE":
            if c.value.strip().startswith("@"):
                p.media.append(_strip_xref(c.value))
        elif c.tag == "FAMC":
            p.families_as_child.append(_strip_xref(c.value))
        elif c.tag == "FAMS":
            p.families_as_spouse.append(_strip_xref(c.value))
    return p


def _parse_family(rec: RawRecord) -> Family:
    f = Family(xref=rec.xref)
    for c in rec.children:
        if c.tag == "HUSB":
            f.husband = _strip_xref(c.value)
        elif c.tag == "WIFE":
            f.wife = _strip_xref(c.value)
        elif c.tag == "CHIL":
            f.children.append(_strip_xref(c.value))
        elif c.tag in EVENT_TAGS:
            f.events.append(_parse_event(c))
        elif c.tag == "NOTE":
            _note_targets(c, f)
        elif c.tag == "SOUR":
            if c.value.strip().startswith("@"):
                f.sources.append(_strip_xref(c.value))
        elif c.tag == "OBJE":
            if c.value.strip().startswith("@"):
                f.media.append(_strip_xref(c.value))
    return f


def _parse_source(rec: RawRecord) -> SourceRecord:
    src = SourceRecord(xref=rec.xref)
    for c in rec.children:
        if c.tag == "TITL":
            src.title = _combined_value(c)
        elif c.tag == "AUTH":
            src.author = c.value
        elif c.tag == "PUBL":
            src.publication = c.value
        elif c.tag == "PAGE":
            src.page = c.value
    return src


def _parse_media(rec: RawRecord) -> MediaRecord:
    med = MediaRecord(xref=rec.xref)
    file_rec = rec.child("FILE")
    if file_rec:
        med.file = _combined_value(file_rec)
    titl = rec.child("TITL")
    if titl:
        med.title = _combined_value(titl)
    return med


def _parse_note(rec: RawRecord) -> NoteRecord:
    note = NoteRecord(xref=rec.xref)
    note.text = _combined_value(rec)
    return note


def _convert(roots: list[RawRecord]) -> GedcomDocument:
    doc = GedcomDocument()
    for rec in roots:
        if rec.tag == "INDI":
            doc.persons.append(_parse_person(rec))
        elif rec.tag == "FAM":
            doc.families.append(_parse_family(rec))
        elif rec.tag == "SOUR":
            src = _parse_source(rec)
            doc.sources[src.xref] = src
        elif rec.tag == "OBJE":
            med = _parse_media(rec)
            doc.media[med.xref] = med
        elif rec.tag == "NOTE":
            note = _parse_note(rec)
            doc.notes[note.xref] = note
    return doc
