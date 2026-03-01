"""Entry point for the backend service."""

from fastapi import FastAPI
from . import service

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
