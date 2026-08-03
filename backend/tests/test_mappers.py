"""Tests de mappers ORM <-> Domain.

Aquests tests SÍ fan servir SQLite en memòria (posant dades a l'ORM per
verificar la conversió). Només els tests de *domínio pur* es mantenen
sense SQLite.
"""

from __future__ import annotations

from app.domain.entities import Event as DomainEvent
from app.domain.entities import Family as DomainFamily
from app.domain.entities import Person as DomainPerson
from app.domain.entities import Place as DomainPlace
from app.mappers import EventMapper, FamilyMapper, PersonMapper, PlaceMapper


def test_person_to_domain(test_session):
    from app.models import Person

    orm = Person(xref="I1", given_name="Joan", surname="Miró", uuid="u-1")
    test_session.add(orm)
    test_session.commit()

    domain = PersonMapper.to_domain(orm)
    assert isinstance(domain, DomainPerson)
    assert domain.xref == "I1"
    assert domain.given_name == "Joan"
    assert domain.uuid == "u-1"
    assert domain.id == orm.id


def test_person_to_orm_creates_and_reuses(test_session):
    domain = DomainPerson(xref="I2", given_name="Anna", surname="Puig")

    orm = PersonMapper.to_orm(domain)
    assert orm.xref == "I2"
    test_session.add(orm)
    test_session.commit()

    # Reutilitza la mateixa instància (identitat preservada).
    same = PersonMapper.to_orm(domain, orm)
    assert same is orm


def test_family_mapper_roundtrip(test_session):
    from app.models import Family

    orm = Family(xref="F1", marriage_date="1900-01-01")
    test_session.add(orm)
    test_session.commit()

    domain = FamilyMapper.to_domain(orm)
    assert isinstance(domain, DomainFamily)
    assert domain.xref == "F1"

    back = FamilyMapper.to_orm(domain, orm)
    assert back is orm


def test_place_mapper_roundtrip(test_session):
    from app.models import Place

    orm = Place(name="Barcelona", display_name="Barcelona", country="ES")
    test_session.add(orm)
    test_session.commit()

    domain = PlaceMapper.to_domain(orm)
    assert isinstance(domain, DomainPlace)
    assert domain.country == "ES"

    back = PlaceMapper.to_orm(domain, orm)
    assert back is orm


def test_event_mapper_roundtrip(test_session):
    from app.models import Event

    orm = Event(event_type="birth", date_text="10 FEB 1890")
    test_session.add(orm)
    test_session.commit()

    domain = EventMapper.to_domain(orm)
    assert isinstance(domain, DomainEvent)
    assert domain.event_type == "birth"

    back = EventMapper.to_orm(domain, orm)
    assert back is orm
