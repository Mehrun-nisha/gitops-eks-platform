from app import app


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_returns_version():
    resp = client().get("/")
    assert resp.status_code == 200
    assert "version" in resp.get_json()


def test_health_and_ready():
    c = client()
    assert c.get("/healthz").status_code == 200
    assert c.get("/readyz").status_code == 200


def test_metrics_exposes_request_counter():
    c = client()
    c.get("/")
    body = c.get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in body
