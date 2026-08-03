"""Tests dels nous endpoints de qualitat/intel·ligència genealògica."""

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


def test_quality_report_endpoint(client):
    _import(client)
    r = client.get("/api/quality/report")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 0
    assert isinstance(body["errors"], list)
    assert isinstance(body["warnings"], list)
    assert isinstance(body["infos"], list)


def test_quality_report_markdown(client):
    _import(client)
    r = client.get("/api/quality/report?format=markdown")
    assert r.status_code == 200
    assert "# Informe" in r.json()["report"]


def test_quality_report_bad_format(client):
    r = client.get("/api/quality/report?format=xml")
    assert r.status_code == 422


def test_person_quality_endpoint(client):
    _import(client)
    persons = client.get("/api/persons").json()
    pid = persons[0]["id"]
    r = client.get(f"/api/quality/person/{pid}")
    assert r.status_code == 200
    body = r.json()
    assert body["person_id"] == pid
    assert "score" in body
    assert "factors" in body


def test_person_quality_not_found(client):
    _import(client)
    r = client.get("/api/quality/person/99999")
    assert r.status_code == 404


def test_duplicates_endpoint(client):
    _import(client)
    r = client.get("/api/duplicates")
    assert r.status_code == 200
    dups = r.json()
    assert isinstance(dups, list)
    assert len(dups) >= 1
    assert dups[0]["person_a"]["name"] == "John Garcia"


def test_statistics_endpoint(client):
    _import(client)
    r = client.get("/api/statistics")
    assert r.status_code == 200
    body = r.json()
    assert body["persons"] == 3
    assert body["males"] == 2
    assert body["females"] == 1
    assert body["sex_by"]["M"] == 2


def test_research_tasks_endpoint(client):
    _import(client)
    r = client.get("/api/research/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)
    assert all("objective" in t for t in tasks)


def test_research_tasks_limit(client):
    _import(client)
    r = client.get("/api/research/tasks?limit=1")
    assert r.status_code == 200
    assert len(r.json()) <= 1
