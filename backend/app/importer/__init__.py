"""Importador de fitxers GEDCOM.

Of ofer una API publica per a parsejar GEDCOM 5.5.1 a objectes Python
(`app.importer.models`). L'escriptura a la base de dades es deixa a una
fase posterior.
"""

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
from app.importer.parser import GedcomParseError, parse, read_lines

__all__ = [
    "Event",
    "Family",
    "GedcomDocument",
    "GedcomParseError",
    "MediaRecord",
    "Name",
    "NoteRecord",
    "Person",
    "SourceRecord",
    "parse",
    "read_lines",
]
