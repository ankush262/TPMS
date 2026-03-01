"""Tests for the TPMS backend API endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ═══════════════════════════════════════════════════════════════════
#  Health
# ═══════════════════════════════════════════════════════════════════

def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert isinstance(body["files"], list)
    assert len(body["files"]) > 0


def test_health_lists_file_availability():
    r = client.get("/health")
    body = r.json()
    names = [f["name"] for f in body["files"]]
    assert "tire_intelligence_v1.csv" in names
    assert "maintenance_report_v1.csv" in names
    assert "model.info.json" in names


# ═══════════════════════════════════════════════════════════════════
#  Intelligence
# ═══════════════════════════════════════════════════════════════════

def test_intelligence_returns_json_array():
    r = client.get("/intelligence")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_intelligence_has_required_keys():
    r = client.get("/intelligence")
    data = r.json()
    required = {"vehicle_id", "stress_score", "risk_level",
                "recommended_action", "priority_rank"}
    for row in data:
        assert required.issubset(row.keys()), f"Missing keys in {row.keys()}"


def test_stress_score_in_range():
    r = client.get("/intelligence")
    for row in r.json():
        ss = float(row["stress_score"])
        assert 0 <= ss <= 1, f"stress_score={ss} out of [0,1]"


def test_priority_rank_dense():
    r = client.get("/intelligence")
    data = r.json()
    ranks = sorted(int(row["priority_rank"]) for row in data)
    assert ranks == list(range(1, len(ranks) + 1))


# ═══════════════════════════════════════════════════════════════════
#  Report
# ═══════════════════════════════════════════════════════════════════

def test_report_returns_json_array():
    r = client.get("/report")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_report_has_required_keys():
    r = client.get("/report")
    data = r.json()
    if len(data) > 0:
        required = {"vehicle_id", "risk_level", "recommended_action"}
        for row in data:
            assert required.issubset(row.keys())


# ═══════════════════════════════════════════════════════════════════
#  Model info
# ═══════════════════════════════════════════════════════════════════

def test_model_info_returns_json():
    r = client.get("/model-info")
    assert r.status_code == 200
    body = r.json()
    assert "model_version" in body
    assert "formula" in body


# ═══════════════════════════════════════════════════════════════════
#  Downloads
# ═══════════════════════════════════════════════════════════════════

def test_download_csv():
    r = client.get("/download/tire_intelligence_v1.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")


def test_download_json():
    r = client.get("/download/model.info.json")
    assert r.status_code == 200
    assert "application/json" in r.headers.get("content-type", "")


def test_download_invalid_returns_404():
    r = client.get("/download/nonexistent_file.csv")
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════
#  Validate
# ═══════════════════════════════════════════════════════════════════

def test_validate_endpoint():
    r = client.get("/validate")
    assert r.status_code == 200
    body = r.json()
    assert "valid" in body
    assert "issues" in body
    assert body["valid"] is True, f"Validation failed: {body['issues']}"


# ═══════════════════════════════════════════════════════════════════
#  Raw / Processed config
# ═══════════════════════════════════════════════════════════════════

def test_raw_config():
    r = client.get("/raw-config")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "vehicle_id" in data[0]


def test_processed_config():
    r = client.get("/processed-config")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "vehicle_id" in data[0]
        assert "load_per_wheel" in data[0]
