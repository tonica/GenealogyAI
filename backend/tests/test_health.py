def test_read_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "GenealogyAI"


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["app"] == "GenealogyAI"
