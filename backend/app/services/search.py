"""Serveis de preparació i indexació per a la cerca.

Conté:
  - `soundex` i `metaphone`: algoritmes fonètics per aproximar paraules
    que sonen igual (només es prepafen; la integració es farà servir en el
    futur motor de recerca).
  - `PersonFtsIndexer` (SearchIndexer): taula FTS5 per a `persons`.
"""

from __future__ import annotations

import re
import unicodedata

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.person import Person

logger = get_logger("search")

_SOUNDEX_CODES = ["BFPV", "CGJKQSXZ", "DT", "L", "MN", "R"]


def _strip_accents(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def _soundex_code(ch: str) -> str:
    for idx, group in enumerate(_SOUNDEX_CODES, start=1):
        if ch in group:
            return str(idx)
    return ""


def _soundex_char(ch: str) -> str:
    upper = ch.upper()
    for idx, group in enumerate(_SOUNDEX_CODES, start=1):
        if upper in group:
            return str(idx)
    return ""


def soundex(word: str | None) -> str | None:
    """Soundex (4 caracters) d'un mot; None si buit.

    Exemple: 'Garcia' -> 'G620'. Sola identificar noms que sonen igual.
    """
    if word is None:
        return None
    value = re.sub(r"[^a-z]", "", _strip_accents(word).lower())
    if not value:
        return None
    first = value[0]
    code = first.upper()
    previous = _soundex_char(first)
    for ch in value[1:]:
        digit = _soundex_char(ch)
        if digit and digit != previous:
            code += digit
            if len(code) >= 4:
                break
        previous = digit
    return (code + "000")[:4]


def metaphone(word: str | None) -> str | None:
    """Metaphone simplificat (versió primitiva per a futura integració).

    De moment es un pas net d'accents minuscules, deixant la taula de
    transformacions sencera per a la fase del motor de recerca.
    """
    if word is None:
        return None
    return re.sub(r"[^a-z]", "", _strip_accents(word).lower()) or None


class SearchIndexer:
    """Índex FTS5 (full-text search) sobre la taula `persons`.

    La taula virtual `person_fts` indexa nom, cognoms i `search_name` de
    cada persona per permetre cerques ràpides i tolerants a accents.
    """

    # Motor extern column mapping: `docid` es la PK de `persons`.
    CREATE_SQL = """CREATE VIRTUAL TABLE IF NOT EXISTS person_fts USING fts5(
        given_name,
        surname,
        search_name,
        content='persons',
        content_rowid='id'
    )"""

    SYNC_SQL = """INSERT INTO person_fts(rowid, given_name, surname, search_name)
        SELECT id, given_name, surname, search_name FROM persons"""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.fts_table = "person_fts"

    def ensure_schema(self) -> None:
        """Crea la taula FTS5 si no existeix."""
        self.session.execute(text(self.CREATE_SQL))

    def rebuild(self) -> int:
        """Reconstrueix l'índex des de `persons`.

        Usa la comanda especial `rebuild` d'FTS5, adequada per a taules
        amb `content=` (external content): repobla l'índex a partir dels
        continguts actuals. `DELETE FROM person_fts` no aplica a
        external-content (rebota amb SQLite).
        """
        self.ensure_schema()
        self.session.execute(
            text(f"INSERT INTO {self.fts_table}({self.fts_table}) VALUES('rebuild')")
        )
        count = self.session.execute(
            text(f"SELECT COUNT(*) FROM {self.fts_table}")
        ).scalar()
        logger.info("fts rebuilt count=%s", count)
        return int(count or 0)

    def search(self, query: str, limit: int = 50) -> list[Person]:
        """Busca persones per text a l'índex FTS5 (retorna ORM).

        No s'ha d'usar encara des de l'API (reservat per al motor de cerca).
        """
        if not query.strip():
            return []
        q = query.replace('"', " ").strip()
        stmt = text(
            "SELECT rowid FROM {fts} WHERE {fts} MATCH :q LIMIT :lim".format(
                fts=self.fts_table
            )
        )
        rows = self.session.execute(stmt, {"q": q, "lim": limit}).fetchall()
        ids = [r[0] for r in rows]
        if not ids:
            return []
        persons = self.session.query(Person).filter(Person.id.in_(ids)).all()
        by_id = {p.id: p for p in persons}
        # Preserva l'ordre de rellevància del FTS.
        return [by_id[i] for i in ids if i in by_id]
