"""Tests de l'API REST."""

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
1 NAME Maria /Perez/
1 SEX F
1 BIRT
2 DATE 3 JUN 1895
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I1@
0 TRLR
"""


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


def _import(client, raw: bytes, name: str = "arbre.ged"):
    return client.post(
        "/api/import",
        files={"file": (name, raw, "text/plain")},
    )


def test_import_then_full_api_flow(client):
    r = _import(client, GED.encode())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["persons"] == 2
    assert body["stats"]["sex_by"]["M"] == 1

    r = client.get("/api/persons")
    assert r.status_code == 200
    persons = r.json()
    assert len(persons) == 2
    assert {p["surname"] for p in persons} == {"Garcia", "Perez"}

    pid = persons[0]["id"]
    r = client.get(f"/api/person/{pid}")
    assert r.status_code == 200
    assert "events" in r.json()

    assert client.get("/api/person/99999").status_code == 404

    r = client.get("/api/families")
    assert r.status_code == 200
    fam = r.json()
    assert len(fam) == 1
    assert fam[0]["father"] is not None
    assert len(fam[0]["children"]) == 1

    assert client.get("/api/places").status_code == 200

    r = client.get(f"/api/tree/{pid}?depth=3")
    assert r.status_code == 200
    assert r.json()["root"]["id"] == pid

    r = client.get("/api/persons?q=garcia")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_import_normalizes_persons(client):
    _import(client, GED.encode())
    r = client.get("/api/persons")
    perado = r.json()
    by_surname = {p["surname"]: p for p in perado}
    assert by_surname["Garcia"]["given_name"] == "John"
    assert by_surname["Perez"]["given_name"] == "Maria"


def test_import_rejects_empty_file(client):
    resp = _import(client, b"")
    assert resp.status_code == 400


def test_import_rejects_invalid_gedcom(client):
    resp = _import(client, b"AQUESTA LINIA NO TE NIVELL")
    assert resp.status_code == 422
