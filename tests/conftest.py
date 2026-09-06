"""Configuracion compartida de los tests.

Cada test corre contra una base de datos SQLite en memoria totalmente
aislada: se crea antes del test y se destruye despues.

(La variable SECRET_KEY para los tests se define en el conftest.py de la
raiz del repo, que pytest carga antes que este.)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401  -> registra los modelos en Base.metadata
from app.api.deps import get_db
from app.db.base import Base
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _new_test_client() -> TestClient:
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def raw_client():
    """Cliente SIN autenticar: para probar registro, login y casos 401."""
    with _new_test_client() as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _register_and_login(client: TestClient, email: str, password: str = "supersecret") -> str:
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture
def client(raw_client):
    """Cliente ya autenticado con un usuario de prueba (el caso comun)."""
    token = _register_and_login(raw_client, "user@example.com")
    raw_client.headers["Authorization"] = f"Bearer {token}"
    return raw_client


@pytest.fixture
def other_client():
    """Un segundo usuario, para probar que no ve los datos del primero."""
    with _new_test_client() as test_client:
        token = _register_and_login(test_client, "otro@example.com")
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def category_id(client) -> int:
    """Crea una categoria de apoyo (del usuario autenticado) y devuelve su id."""
    return client.post("/api/v1/categories", json={"name": "Comida"}).json()["id"]
