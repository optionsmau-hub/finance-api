"""Tests a nivel de la aplicacion: raiz, CORS y validacion de configuracion."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_root_endpoint(raw_client):
    response = raw_client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_endpoint(raw_client):
    assert raw_client.get("/health").json() == {"status": "ok"}


def test_cors_preflight_is_allowed(raw_client):
    # Un navegador manda primero una peticion OPTIONS ("preflight") para
    # preguntar si tiene permiso. La debe responder el middleware de CORS.
    response = raw_client.options(
        "/api/v1/categories",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_settings_rejects_dev_secret_in_production():
    with pytest.raises(ValidationError):
        Settings(debug=False, secret_key="dev-secret-change-me-in-production-0123456789")


def test_settings_allows_dev_secret_in_debug():
    settings = Settings(debug=True, secret_key="dev-secret-change-me-in-production-0123456789")
    assert settings.debug is True


def test_cors_origins_list_splits_comma_separated_value():
    settings = Settings(secret_key="x" * 40, cors_origins="http://a.com, http://b.com")
    assert settings.cors_origins_list == ["http://a.com", "http://b.com"]
