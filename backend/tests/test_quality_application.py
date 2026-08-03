"""Tests de l'application layer: DomainLoader i use cases de qualitat.

Usen el fixture `test_session` (SQLite en memòria) amb dades ORM reals.
"""

from __future__ import annotations

import pytest

from app.application.domain_loader import DomainLoader
from app.application.services.quality import (
    DuplicatesUseCase,
    PersonQualityUseCase,
    QualityReportUseCase,
    ResearchTasksUseCase,
    StatisticsUseCase,
)
from app.application.unit_of_work import UnitOfWork
from app.models import Event, Family, ParentChild, Person, Place


def _seed_person(session, xref, given, surname, sex="M"):
    p = Person(xref=xref, given_name=given, surname=surname, sex=sex)
    session.add(p)
    session.flush()
    return p


def _seed_event(session, person, etype, date_text, place=None):
    ev = Event(event_type=etype, date_text=date_text, person_id=person.id)
    if place is not None:
        ev.place = place
    session.add(ev)
    session.flush()
    return ev


class TestDomainLoader:
    def test_load_empty(self, test_session):
        ds = DomainLoader(UnitOfWork(test_session)).load()
        assert ds.persons == []
        assert ds.families == []

    def test_load_persons(self, test_session):
        _seed_person(test_session, "I1", "Joan", "Miró")
        ds = DomainLoader(UnitOfWork(test_session)).load()
        assert len(ds.persons) == 1
        assert ds.persons[0].surname == "Miró"

    def test_derives_birth_from_events(self, test_session):
        p = _seed_person(test_session, "I1", "Joan", "Miró")
        _seed_event(test_session, p, "birth", "12 JAN 1893")
        ds = DomainLoader(UnitOfWork(test_session)).load()
        assert ds.persons[0].birth_date == "12 JAN 1893"

    def test_derives_death_from_events(self, test_session):
        p = _seed_person(test_session, "I1", "Joan", "Miró")
        _seed_event(test_session, p, "death", "1960")
        ds = DomainLoader(UnitOfWork(test_session)).load()
        assert ds.persons[0].death_date == "1960"

    def test_child_links(self, test_session):
        father = _seed_person(test_session, "I1", "Joan", "Miró")
        child = _seed_person(test_session, "I2", "Pere", "Miró")
        fam = Family(xref="F1", father_id=father.id)
        session_add = test_session
        session_add.add(fam)
        session_add.flush()
        test_session.add(ParentChild(family_id=fam.id, child_id=child.id))
        test_session.commit()

        ds = DomainLoader(UnitOfWork(test_session)).load()
        person = next(p for p in ds.persons if p.xref == "I2")
        assert person.family_as_child_ids == [fam.id]

    def test_places(self, test_session):
        p = _seed_person(test_session, "I1", "Joan", "Miró")
        place = Place(
            name="Barcelona", display_name="Barcelona", canonical_name="barcelona"
        )
        _seed_event(test_session, p, "birth", "1893", place=place)
        ds = DomainLoader(UnitOfWork(test_session)).load()
        assert len(ds.places) == 1
        assert ds.places_raw == ["Barcelona"]


class TestQualityReportUseCase:
    def test_execute(self, test_session):
        p = _seed_person(test_session, "I1", "Joan", "Miró")
        _seed_event(test_session, p, "birth", "12 JAN 1893")
        test_session.commit()

        report = QualityReportUseCase(UnitOfWork(test_session)).execute()
        assert report.to_dict()["total"] >= 0


class TestDuplicatesUseCase:
    def test_finds_duplicates(self, test_session):
        p1 = _seed_person(test_session, "I1", "Joan", "Miró")
        p2 = _seed_person(test_session, "I2", "Joan", "Miró")
        _seed_event(test_session, p1, "birth", "12 JAN 1893")
        _seed_event(test_session, p2, "birth", "12 JAN 1893")
        test_session.commit()
        cands = DuplicatesUseCase(UnitOfWork(test_session)).execute()
        assert len(cands) >= 1


class TestStatisticsUseCase:
    def test_execute(self, test_session):
        p1 = _seed_person(test_session, "I1", "Joan", "Miró", sex="M")
        p2 = _seed_person(test_session, "I2", "Anna", "Puig", sex="F")
        _seed_event(test_session, p1, "birth", "1900")
        _seed_event(test_session, p1, "death", "1960")
        _seed_event(test_session, p2, "birth", "1901")
        test_session.commit()

        stats = StatisticsUseCase(UnitOfWork(test_session)).execute()
        assert stats.persons == 2
        assert stats.males == 1
        assert stats.females == 1
        assert stats.average_age == 60.0


class TestPersonQualityUseCase:
    def test_execute(self, test_session):
        p = _seed_person(test_session, "I1", "Joan", "Miró")
        _seed_event(test_session, p, "birth", "1893")
        test_session.commit()
        result = PersonQualityUseCase(UnitOfWork(test_session)).execute(p.id)
        assert result["person_id"] == p.id
        assert "score" in result

    def test_not_found(self, test_session):
        with pytest.raises(ValueError):
            PersonQualityUseCase(UnitOfWork(test_session)).execute(999_999)


class TestResearchTasksUseCase:
    def test_execute(self, test_session):
        _seed_person(test_session, "I1", "Joan", "Miró")
        test_session.commit()
        tasks = ResearchTasksUseCase(UnitOfWork(test_session)).execute()
        assert tasks
        assert tasks[0].to_dict()["person_id"] == 1

    def test_with_duplicates(self, test_session):
        p1 = _seed_person(test_session, "I1", "Joan", "Miró")
        p2 = _seed_person(test_session, "I2", "Joan", "Miró")
        _seed_event(test_session, p1, "birth", "12 JAN 1893")
        _seed_event(test_session, p2, "birth", "12 JAN 1893")
        test_session.commit()
        dup = DuplicatesUseCase(UnitOfWork(test_session)).execute()
        tasks = ResearchTasksUseCase(UnitOfWork(test_session)).execute(duplicates=dup)
        kinds = {t.kind for t in tasks}
        assert "duplicate" in kinds
