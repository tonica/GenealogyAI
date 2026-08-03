"""Tests del Repository layer (API -> Service -> Repository -> SQLAlchemy)."""

from app.models import Family, Person, Place
from app.repositories import FamilyRepository, PersonRepository, PlaceRepository


def _make_persons(session, count=3):
    for i in range(count):
        session.add(
            Person(
                xref=f"I{i}",
                given_name=f"Nom{i}",
                surname=f"Cog{i}",
                sex="M" if i % 2 else "F",
                search_name=f"Nom{i} Cog{i}",
            )
        )
    session.commit()


def test_person_repository_search_and_get(test_session):
    _make_persons(test_session)
    repo = PersonRepository(test_session)
    # search amb filtre de text
    res = repo.search(q="Nom1")
    assert len(res) == 1
    # search amb filtre de sexe
    males = repo.search(sex="M")
    assert len(males) == 1
    # get by id
    p = res[0]
    assert repo.get(p.id).xref == p.xref
    # count
    assert repo.count() == 3


def test_person_repository_get_models_by_xref_and_uuid(test_session):
    test_session.add(Person(xref="I9", given_name="A", surname="B", uuid="u-xyz"))
    test_session.commit()
    repo = PersonRepository(test_session)
    assert repo.get_by_xref("I9") is not None
    assert repo.get_by_uuid("gg-xyz") is None
    assert repo.get_by_uuid("u-xyz").xref == "I9"


def test_place_repository_crud(test_session):
    test_session.add(
        Place(
            name="Barcelona",
            display_name="Barcelona",
            canonical_name="barcelona",
        )
    )
    test_session.commit()
    repo = PlaceRepository(test_session)
    assert repo.get_by_name("Barcelona") is not None
    assert repo.get_by_canonical_name("barcelona") is not None
    assert repo.count() == 1
    assert len(repo.list(q="bar")) == 1
    assert len(repo.list(q="no-existeix")) == 0


def test_family_repository_list_and_get(test_session):
    test_session.add(Family(xref="F1"))
    test_session.add(Family(xref="F2"))
    test_session.commit()
    repo = FamilyRepository(test_session)
    fams = repo.list_with_members()
    assert len(fams) == 2
    assert repo.get_with_members(fams[0].id).xref in {"F1", "F2"}
    assert repo.count() == 2
