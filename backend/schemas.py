"""Pydantic schemas for the API."""

from pydantic import BaseModel


class SensorData(BaseModel):
    pressure: float
    temperature: float
    timestamp: str
