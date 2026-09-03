"""Punto de entrada de la aplicacion FastAPI.

Arrancar en local:
    uvicorn app.main:app --reload

Documentacion interactiva: http://localhost:8000/docs
"""

from fastapi import FastAPI

from app.api.routes import categories, transactions
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    summary="API para llevar el control de finanzas personales.",
)

app.include_router(categories.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Endpoint simple para verificar que el servicio esta vivo."""
    return {"status": "ok"}
