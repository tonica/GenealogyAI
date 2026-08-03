"""Tests de UUIDMixin aplicat a les entitats i de les PRAGMA de SQLite."""

import uuid

import pytest
from sqlalchemy import create_engine, text

from app.models import Person
from app.models.mixins import UUIDMixin


def test_uuid_mixin_generates_valid_uuid(test_session):
    p = Person(xref="I1", given_name="A", surname="B")
    test_session.add(p)
    test_session.commit()
    uid = uuid.UUID(p.uuid)
    assert str(uid) == p.uuid


def test_uuid_unique_across_entities(test_session):
    """UUIDs de Person, Family i Place no col·lideixen (volum baix)."""
    from app.models import Family, Place
    from app.repositories import FamilyRepository, PlaceRepository

    test_session.add_all(
        [
            Person(xref="I1", given_name="A", surname="B"),
            Family(xref="F1"),
            Place(name="Barcelona", display_name="Barcelona"),
        ]
    )
    test_session.commit()
    fam = FamilyRepository(test_session).list_with_members()[0]
    place = PlaceRepository(test_session).list()[0]
    person_uuids = [p.uuid for p in test_session.query(Person)]
    all_uuids = [fam.uuid, place.uuid] + person_uuids
    assert len(all_uuids) == len(set(all_uuids))


def test_mixin_present_in_models():
    from app.models import AuditLog, Family, Person, Place

    for cls in (AuditLog, Family, Person, Place):
        assert issubclass(cls, UUIDMixin)


@pytest.mark.skipif(
    not str(__import__("app.db.session", fromlist=["engine"]).engine.url).startswith(
        "sqlite"
    ),
    reason="Només aplica a SQLite",
)
def test_sqlite_pragmas_applied():
    """Verifica que les PRAGMA es mostren actives a una connexió SQLite."""
    from sqlalchemy import event

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    PRAGMAS = [
        ("journal_mode", "memory"),  # SQLite en memòria
        ("foreign_keys", "1"),
        ("synchronous", "1"),  # NORMAL == 1
        ("temp_store", "2"),  # MEMORY == 2
    ]

    from app.db.session import _configure_sqlite_pragmas

    event.listens_for(engine, "connect")(_configure_sqlite_pragmas)
    with engine.connect() as conn:
        for pragma, expected in PRAGMAS:
            value = conn.execute(text(f"PRAGMA {pragma}")).scalar()
            assert (
                str(value).lower() == expected.lower()
            ), f"pragma {pragma} = {value} (esperat {expected})"
