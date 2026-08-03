"""Tests de les entitats de domini (pures, sense infraestructura)."""

from __future__ import annotations

from app.domain.entities import (
    Event,
    Family,
    Media,
    Person,
    Place,
    ResearchTask,
    Source,
    Suggestion,
)


def test_person_display_name():
    assert Person(given_name="Joan", surname="Miró").display_name == "Joan Miró"
    assert Person(surname="Miró").display_name == "Miró"
    assert Person(xref="@I1@").display_name == "@I1@"


def test_person_add_event_dedupes():
    p = Person(id=1)
    p.add_event(10)
    p.add_event(10)
    p.add_event(11)
    assert p.event_ids == [10, 11]


def test_family_children():
    f = Family(id=1)
    f.add_child(3)
    f.add_child(3)
    f.add_child(4)
    assert f.child_ids == [3, 4]


def test_place_value_object():
    p = Place(name="Barcelona", display_name="Barcelona, Cataluña")
    assert p.name_value.display == "Barcelona, Cataluña"


def test_entities_are_dataclasses():
    import dataclasses

    for cls in (Person, Family, Place, Event, Source, Media, Suggestion, ResearchTask):
        assert dataclasses.is_dataclass(cls), cls.__name__
