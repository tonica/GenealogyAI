"""Tests del contracte públic v1 (DTOs) exposat sota /api/v1.

Verifica que els endpoints retornen exactament els DTOs definits a
`app.schemas.dto` i que el contracte no retorna mai objectes ORM.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

GED = """0 HEAD
0 @I1@ INDI
1 NAME John /Garcia/
1 SEX M
1 BIRT
2 DATE 10 FEB 1890
2 PLAC Barcelona
0 @I2@ INDI
1 NAME John /Garcia/
1 SEX M
1 BIRT
2 DATE 10 FEB 1890
2 PLAC Barcelona
0 @I3@ INDI
1 NAME Maria /Perez/
1 SEX F
1 BIRT
2 DATE 3 JUN 1895
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I3@
1 CHIL @I2@
0 TRLR
"""

EXPECTED_KEYS = {
    "id",
    "xref",
    "given_name",
    "surname",
    "prefix",
    "suffix",
    "sex",
    "display_name",
    "birth_date",
    "death_date",
    "birth_year",
    "death_year",
    "birth_place",
    "death_place",
    "quality",
}


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()


def _import(client):
    return client.post(
        "/api/import",
        files={"file": ("arbre.ged", GED.encode(), "text/plain")},
    )


def test_v1_persons_search(client):
    _import(client)
    r = client.get("/api/v1/persons")
    assert r.status_code == 200
    persons = r.json()
    assert len(persons) == 3
    assert EXPECTED_KEYS == set(persons[0].keys())
    by_surname = {p["surname"]: p for p in persons}
    assert by_surname["Garcia"]["given_name"] == "John"
    assert by_surname["Garcia"]["birth_year"] == 1890
    assert by_surname["Garcia"]["birth_place"] == "Barcelona"


def test_v1_persons_filters(client):
    _import(client)
    assert len(client.get("/api/v1/persons?q=maria").json()) == 1
    assert len(client.get("/api/v1/persons?sex=M").json()) == 2
    assert len(client.get("/api/v1/persons?sex=F").json()) == 1
    assert len(client.get("/api/v1/persons?birth_year=1895").json()) == 1
    assert len(client.get("/api/v1/persons?birth_year=1900").json()) == 0
    assert len(client.get("/api/v1/persons?surname=perez").json()) == 1
    assert len(client.get("/api/v1/persons?place=barcelona").json()) == 2


def test_v1_persons_pagination(client):
    _import(client)
    r = client.get("/api/v1/persons?limit=2&offset=0")
    assert len(r.json()) == 2


def test_v1_person_detail(client):
    _import(client)
    persons = client.get("/api/v1/persons").json()
    pid = persons[0]["id"]
    r = client.get(f"/api/v1/persons/{pid}")
    assert r.status_code == 200
    body = r.json()
    for key in EXPECTED_KEYS:
        assert key in body
    assert "parents" in body
    assert "spouses" in body
    assert "children" in body
    assert "timeline" in body
    assert "quality_detail" in body
    assert "duplicates" in body
    assert "tasks" in body


def test_v1_person_detail_not_found(client):
    _import(client)
    r = client.get("/api/v1/persons/99999")
    assert r.status_code == 404


def test_v1_families(client):
    _import(client)
    r = client.get("/api/v1/families")
    assert r.status_code == 200
    fams = r.json()
    assert len(fams) == 1
    fam = fams[0]
    assert set(fam.keys()) == {
        "id",
        "xref",
        "father",
        "mother",
        "children",
        "marriage_date",
        "marriage_place",
        "events",
    }
    assert fam["father"]["surname"] == "Garcia"
    assert len(fam["children"]) == 1


def test_v1_family_detail(client):
    _import(client)
    fams = client.get("/api/v1/families").json()
    fid = fams[0]["id"]
    r = client.get(f"/api/v1/families/{fid}")
    assert r.status_code == 200
    assert r.json()["id"] == fid
    assert client.get("/api/v1/families/99999").status_code == 404


def test_v1_statistics(client):
    _import(client)
    r = client.get("/api/v1/statistics")
    assert r.status_code == 200
    body = r.json()
    assert body["persons"] == 3
    assert body["males"] == 2
    assert body["females"] == 1


def test_v1_quality_report(client):
    _import(client)
    r = client.get("/api/v1/quality/report")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"total", "errors", "warnings", "infos"}
    assert body["total"] >= 0


def test_v1_person_quality(client):
    _import(client)
    persons = client.get("/api/v1/persons").json()
    pid = persons[0]["id"]
    r = client.get(f"/api/v1/quality/persons/{pid}")
    assert r.status_code == 200
    body = r.json()
    assert body["person_id"] == pid
    assert "score" in body
    assert "factors" in body


def test_v1_duplicates(client):
    _import(client)
    r = client.get("/api/v1/duplicates")
    assert r.status_code == 200
    dups = r.json()
    assert len(dups) >= 1
    assert set(dups[0].keys()) == {
        "person_a",
        "person_b",
        "score",
        "confidence",
        "rules_used",
        "reasons",
    }


def test_v1_research_tasks(client):
    _import(client)
    r = client.get("/api/v1/research/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)
    assert all(
        {"person_id", "xref", "objective", "kind", "hypothesis", "related_person_ids"}
        <= set(t.keys())
        for t in tasks
    )


def test_v1_dashboard(client):
    _import(client)
    r = client.get("/api/v1/dashboard")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {
        "persons",
        "families",
        "events",
        "places",
        "sources",
        "media",
        "males",
        "females",
        "average_age",
        "average_quality",
        "duplicates",
        "pending_tasks",
        "last_import",
    }
    assert body["persons"] == 3
    assert body["families"] == 1
    assert body["duplicates"] >= 1
    assert body["pending_tasks"] >= 0


def test_v1_coexists_with_v0(client):
    """El contracte v1 no trenca ni elimina l'API original /api."""
    _import(client)
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/persons").status_code == 200
    assert client.get("/api/v1/persons").status_code == 200
