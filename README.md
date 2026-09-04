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
| Autenticación | JWT (PyJWT) + contraseñas con bcrypt |
| Presupuestos y reportes | Agregaciones SQL (`SUM` / `GROUP BY`) |
| Base de datos | PostgreSQL (SQLite para desarrollo rápido) |
| Tests | pytest + pytest-cov |
| Lint / formato | Ruff + pre-commit |
| Contenedores | Docker + docker-compose (app + PostgreSQL) |
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

# 6. (opcional, recomendado) hook de git que corre el lint antes de cada commit
pre-commit install
```

Abre la documentación interactiva en <http://localhost:8000/docs>.

### Autenticación

La API requiere estar logueado para usar categorías y transacciones:

1. `POST /api/v1/auth/register` con `{"email": "...", "password": "..."}`.
2. `POST /api/v1/auth/login` (formulario, no JSON) con `username` = tu email y `password`.
   Devuelve un `access_token`.
3. Mandas ese token en cada petición: header `Authorization: Bearer <token>`.

En `/docs` hay un botón **Authorize** arriba a la derecha: pega ahí el token (sin
la palabra `Bearer`) y todos los endpoints protegidos quedan autenticados automáticamente
para probarlos desde el navegador.

### Correr todo con Docker

Con Docker Desktop instalado, esto levanta la API **y** PostgreSQL, aplica las
migraciones y deja todo listo en <http://localhost:8000/docs>:

```bash
docker compose up --build
```

> Nota: este Dockerfile/compose sigue las practicas estandar (imagen `slim`,
> capas cacheables, healthcheck de la base de datos) pero no se ha podido
> probar en esta maquina en particular por no tener Docker instalado.
> Si algo no arranca a la primera, revisa `docker compose logs app`.

### Usar PostgreSQL sin Docker (para la app, si igual quieres SQLite en la app)

Si solo quieres la base de datos en Docker y correr la API tu mismo:

```bash
docker compose up db -d
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

Con reporte de cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

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

| Método | Ruta | Descripción | Requiere token |
|--------|------|-------------|:---:|
| GET | `/health` | Estado del servicio | No |
| POST | `/api/v1/auth/register` | Crear una cuenta | No |
| POST | `/api/v1/auth/login` | Iniciar sesión, devuelve un token | No |
| GET | `/api/v1/categories` | Listar categorías | Sí |
| POST | `/api/v1/categories` | Crear categoría | Sí |
| GET | `/api/v1/categories/{id}` | Obtener una categoría | Sí |
| PATCH | `/api/v1/categories/{id}` | Actualizar una categoría | Sí |
| DELETE | `/api/v1/categories/{id}` | Eliminar una categoría (409 si tiene movimientos) | Sí |
| GET | `/api/v1/transactions` | Listar movimientos (filtros: `category_id`, `type`, `date_from`, `date_to`) | Sí |
| POST | `/api/v1/transactions` | Registrar un ingreso o gasto | Sí |
| GET | `/api/v1/transactions/{id}` | Obtener un movimiento | Sí |
| PATCH | `/api/v1/transactions/{id}` | Actualizar un movimiento | Sí |
| DELETE | `/api/v1/transactions/{id}` | Eliminar un movimiento | Sí |
| GET | `/api/v1/budgets` | Listar presupuestos (filtro: `month`) | Sí |
| POST | `/api/v1/budgets` | Crear un presupuesto (categoría + mes + límite) | Sí |
| GET | `/api/v1/budgets/{id}` | Obtener un presupuesto | Sí |
| PATCH | `/api/v1/budgets/{id}` | Ajustar el límite de un presupuesto | Sí |
| DELETE | `/api/v1/budgets/{id}` | Eliminar un presupuesto | Sí |
| GET | `/api/v1/reports/summary?month=YYYY-MM` | Total de ingresos, gastos y balance del mes | Sí |
| GET | `/api/v1/reports/by-category?month=YYYY-MM` | Total por categoría, de mayor a menor (filtro opcional `type`) | Sí |
| GET | `/api/v1/reports/budget-status?month=YYYY-MM` | Gasto vs. límite por categoría presupuestada | Sí |

## Roadmap

Ver [PLAN.md](PLAN.md) para las siguientes etapas (transacciones, autenticación con JWT,
presupuestos, reportes, Docker y despliegue).
