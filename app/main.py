"""Punto de entrada de la aplicacion FastAPI.

Arrancar en local:
    uvicorn app.main:app --reload

Documentacion interactiva: http://localhost:8000/docs
"""

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.api.routes import auth, budgets, categories, reports, transactions
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("finance_api")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    summary="API para llevar el control de finanzas personales.",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(budgets.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Deja un renglon de log por cada peticion: metodo, ruta, status y
    cuanto tardo. Es lo primero que revisas cuando algo en produccion se
    porta raro y no tienes forma de reproducirlo a mano.
    """
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Red de seguridad: si algo revienta que no anticipamos (un bug, la
    base de datos caida), el usuario recibe un 500 con un mensaje generico
    -- no un stack trace de Python -- y nosotros el detalle en el log.
    """
    logger.exception("Error no manejado en %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Endpoint simple para verificar que el servicio esta vivo."""
    return {"status": "ok"}
