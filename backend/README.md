# TPMS Backend API

A lightweight FastAPI service that serves the enriched tire-intelligence CSVs as JSON endpoints and provides file downloads.

## Quick start

```bash
cd E:\TPMS
pip install fastapi "uvicorn[standard]"
python -m uvicorn backend.main:app --reload --port 8000
```

Then open **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health + file availability |
| `GET` | `/intelligence` | `tire_intelligence_v1.csv` as JSON array |
| `GET` | `/report` | `maintenance_report_v1.csv` as JSON array |
| `GET` | `/model-info` | `model.info.json` content |
| `GET` | `/raw-config` | Raw `configuration_data.csv` as JSON |
| `GET` | `/processed-config` | Cleaned config CSV as JSON |
| `GET` | `/download/{filename}` | Download a CSV/JSON file |
| `GET` | `/validate` | Run sanity checks on intelligence data |

### Response shapes

**`GET /intelligence`** returns:
```json
[
  {
    "vehicle_id": "MH47MD4509",
    "vehicle_type": "Box Van",
    "stress_score": 0.693,
    "risk_level": "Moderate",
    "recommended_action": "Schedule maintenance check",
    "priority_rank": 1,
    ...
  },
  ...
]
```

**`GET /health`** returns:
```json
{
  "status": "ok",
  "files": [
    { "name": "tire_intelligence_v1.csv", "exists": true },
    ...
  ]
}
```

## Docker

```bash
docker compose up backend
```

The service runs on port **8000** inside the container.
