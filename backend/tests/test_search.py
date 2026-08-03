"""Tests de l'índex FTS5 (SearchIndexer) i dels algoritmes fonètics."""

from app.models import Person
from app.services.search import SearchIndexer, metaphone, soundex


def test_soundex_basic():
    assert soundex("Garcia") == "G620"
    assert soundex("Robert") == "R163"
    assert soundex("") is None
    assert soundex(None) is None


def test_soundex_similar_names():
    assert soundex("Smith") == soundex("Smyth")


def test_metaphone_simple():
    assert metaphone("Álaz") == "alaz"
    assert metaphone("Toni") == "toni"
    assert metaphone(None) is None


def test_fts_rebuild_and_search(sqlite_session):
    sqlite_session.add_all(
        [
            Person(xref="I1", given_name="Maria", surname="Garcia"),
            Person(xref="I2", given_name="Toni", surname="Carbonell"),
            Person(xref="I3", given_name="Tona", surname="Carbonera"),
        ]
    )
    sqlite_session.commit()

    indexer = SearchIndexer(sqlite_session)
    assert indexer.rebuild() == 3
    assert len(indexer.search("Maria")) == 1
    assert len(indexer.search("Carbonell")) == 1
    assert indexer.search("") == []


def test_fts_rebuild_idempotent(sqlite_session):
    sqlite_session.add(Person(xref="I9", given_name="Joan", surname="Puig"))
    sqlite_session.commit()
    indexer = SearchIndexer(sqlite_session)
    assert indexer.rebuild() == 1
    assert indexer.rebuild() == 1
