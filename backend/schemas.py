"""Pydantic response models for the TPMS API."""

from pydantic import BaseModel


class HealthFile(BaseModel):
    """Status of a single served file."""
    name: str
    exists: bool


class HealthResponse(BaseModel):
    """GET /health response."""
    status: str
    files: list[HealthFile]


class ErrorResponse(BaseModel):
    """Standard error body."""
    detail: str
