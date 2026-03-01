"""TPMS Backend — FastAPI entry point.

Serves enriched tire-intelligence CSVs as JSON and provides file downloads.
Start locally:
    cd E:\\TPMS
    python -m uvicorn backend.main:app --reload --port 8000
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .schemas import HealthResponse, HealthFile
from .service import (
    SERVED_FILES,
    get_file_status,
    load_csv,
    load_json,
    validate_intelligence,
)

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(levelname)-7s  %(message)s",
)
logger = logging.getLogger("tpms.api")

# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="TPMS Intelligence API",
    version="0.1.0",
    description="Serves tire-intelligence data, maintenance reports, and model metadata.",
)

# CORS — allow local dev origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files at /ui
_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if _FRONTEND_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="ui")


# ── Middleware: request logging ──────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("%s %s", request.method, request.url.path)
    response = await call_next(request)
    return response


# ═══════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health():
    """Service health + which data files are available."""
    file_info = [
        HealthFile(name=name, exists=exists)
        for name, exists in get_file_status().items()
    ]
    return HealthResponse(status="ok", files=file_info)


# ── Intelligence ─────────────────────────────────────────────────────
@app.get("/intelligence", tags=["data"])
def get_intelligence():
    """Return tire_intelligence_v1.csv as a JSON array."""
    return _serve_csv("tire_intelligence_v1.csv", validate=True)


# ── Maintenance report ───────────────────────────────────────────────
@app.get("/report", tags=["data"])
def get_report():
    """Return maintenance_report_v1.csv as a JSON array."""
    return _serve_csv("maintenance_report_v1.csv")


# ── Model info ───────────────────────────────────────────────────────
@app.get("/model-info", tags=["data"])
def get_model_info():
    """Return model.info.json."""
    path = SERVED_FILES.get("model.info.json")
    if path is None or not path.is_file():
        raise HTTPException(404, "model.info.json not found. Run notebook 04 first.")
    return load_json(path)


# ── Raw configuration ────────────────────────────────────────────────
@app.get("/raw-config", tags=["data"])
def get_raw_config():
    """Return the raw configuration_data.csv as JSON."""
    return _serve_csv("configuration_data.csv")


# ── Cleaned / processed ─────────────────────────────────────────────
@app.get("/processed-config", tags=["data"])
def get_processed_config():
    """Return cleaned_configuration_data.csv as JSON."""
    return _serve_csv("cleaned_configuration_data.csv")


# ── File download ────────────────────────────────────────────────────
@app.get("/download/{filename}", tags=["downloads"])
def download_file(filename: str):
    """Download a served CSV or JSON file."""
    path = SERVED_FILES.get(filename)
    if path is None or not path.is_file():
        raise HTTPException(404, f"File '{filename}' not found.")
    media = "text/csv" if filename.endswith(".csv") else "application/json"
    return FileResponse(path, media_type=media, filename=filename)


# ── Validate endpoint ────────────────────────────────────────────────
@app.get("/validate", tags=["ops"])
def validate():
    """Run sanity checks on the intelligence data and return issues."""
    path = SERVED_FILES.get("tire_intelligence_v1.csv")
    if path is None or not path.is_file():
        raise HTTPException(404, "tire_intelligence_v1.csv not found.")
    data = load_csv(path)
    issues = validate_intelligence(data)
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "rows_checked": len(data),
    }


# ── helper ───────────────────────────────────────────────────────────
def _serve_csv(name: str, *, validate: bool = False):
    path = SERVED_FILES.get(name)
    if path is None or not path.is_file():
        raise HTTPException(
            404,
            f"{name} not found. Run the upstream notebook to generate it.",
        )
    data = load_csv(path)
    if validate:
        issues = validate_intelligence(data)
        if issues:
            logger.warning("Validation issues in %s: %s", name, issues)
    return data
