# Finance API

API REST para llevar el control de finanzas personales: categorías, ingresos, gastos,
presupuestos y reportes.

Proyecto de portafolio enfocado en buenas prácticas de backend con Python.

## Stack

| Área | Herramienta |
|------|-------------|
| Framework web | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Validación | Pydantic v2 |
| Base de datos | PostgreSQL (SQLite para desarrollo rápido) |
| Tests | pytest |
| Lint / formato | Ruff |
| CI | GitHub Actions |

## Requisitos

- Python 3.11 o superior (probado con 3.12)
- Opcional: PostgreSQL o Docker (para no usar SQLite)

## Puesta en marcha

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
# source .venv/bin/activate   # macOS / Linux

# 2. Instalar dependencias (incluye herramientas de desarrollo)
pip install -e ".[dev]"

# 3. Configurar variables de entorno
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 4. Crear el esquema de la base de datos
alembic upgrade head

# 5. Arrancar el servidor
uvicorn app.main:app --reload
```

Abre la documentación interactiva en <http://localhost:8000/docs>.

### Usar PostgreSQL en lugar de SQLite

Con Docker:

```bash
docker compose up -d
```

Luego pon en tu `.env`:

```
DATABASE_URL=postgresql+psycopg://finance:finance@localhost:5432/finance_db
```

Y vuelve a ejecutar `alembic upgrade head`.

## Tests

```bash
pytest
```

Los tests usan una base de datos SQLite en memoria, aislada por test. No necesitan
PostgreSQL ni configuración adicional.

## Estructura del proyecto

```
app/
  core/        Configuración (settings, variables de entorno)
  db/          Motor, sesión y clase Base de SQLAlchemy
  models/      Modelos ORM (tablas)
  schemas/     Schemas Pydantic (entrada/salida de la API)
  crud/        Operaciones de base de datos, sin lógica HTTP
  api/
    deps.py    Dependencias reutilizables (sesión de BD, y luego auth)
    routes/    Routers de FastAPI por recurso
  main.py      Creación de la app y registro de routers
alembic/       Migraciones de base de datos
tests/         Tests con pytest
```

## Endpoints actuales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/api/v1/categories` | Listar categorías |
| POST | `/api/v1/categories` | Crear categoría |
| GET | `/api/v1/categories/{id}` | Obtener una categoría |
| PATCH | `/api/v1/categories/{id}` | Actualizar una categoría |
| DELETE | `/api/v1/categories/{id}` | Eliminar una categoría |

## Roadmap

Ver [PLAN.md](PLAN.md) para las siguientes etapas (transacciones, autenticación con JWT,
presupuestos, reportes, Docker y despliegue).
