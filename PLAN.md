# Plan de desarrollo

La idea es construir el proyecto por **etapas cortas**. Cada etapa es una rama +
Pull Request en GitHub, para que tu historial muestre cómo trabajas.

---

## Etapa 0 — Esqueleto (HECHO)

- [x] Estructura de carpetas por capas (core / db / models / schemas / crud / api)
- [x] FastAPI corriendo con endpoint `/health`
- [x] Conexión a base de datos con SQLAlchemy 2.0
- [x] Migraciones con Alembic (`0001_initial`)
- [x] CRUD completo del recurso `Category`
- [x] Tests con pytest (SQLite en memoria)
- [x] CI en GitHub Actions (lint + tests)

## Etapa 1 — Transacciones (ingresos y gastos) (HECHO)

- [x] Modelo `Transaction`: monto, tipo (ingreso/gasto), fecha, nota, `category_id` (FK)
- [x] Relación `Category` 1—N `Transaction` (FK con `ON DELETE RESTRICT`)
- [x] Migración `0002_add_transactions`
- [x] Schemas + CRUD + router `/api/v1/transactions`
- [x] Filtros por rango de fechas, categoría y tipo
- [x] Validación: monto > 0 (`Decimal`, nunca `float`)
- [x] No se puede borrar una categoría con movimientos (409)
- [x] 14 tests nuevos (22 en total)

## Etapa 2 — Usuarios y autenticación (JWT) (HECHO)

- [x] Modelo `User` con contraseña hasheada (bcrypt)
- [x] `POST /api/v1/auth/register` y `POST /api/v1/auth/login` (devuelve access token JWT)
- [x] Dependencia `get_current_user` en `app/api/deps.py`
- [x] Cada categoría y transacción pertenece a un usuario (`owner_id`, FK `RESTRICT`)
- [x] Categorías y transacciones protegidas: cada quien ve y modifica solo lo suyo (404, no 403,
      si intenta acceder a algo de otro usuario)
- [x] Nombre de categoría único por usuario, no global
- [x] Migración `0003_add_users_and_owner_id`
- [x] 11 tests nuevos (33 en total)

## Etapa 3 — Presupuestos y reportes (HECHO)

- [x] Modelo `Budget`: límite mensual por categoría (único por categoría+mes+usuario,
      `ON DELETE CASCADE` si se borra la categoría)
- [x] CRUD `/api/v1/budgets`
- [x] `GET /api/v1/reports/summary?month=YYYY-MM`: total ingresos, gastos, balance
- [x] `GET /api/v1/reports/by-category?month=YYYY-MM`: total agrupado por categoría (SQL
      `SUM`/`GROUP BY`, no en Python), filtro opcional por `type`
- [x] `GET /api/v1/reports/budget-status?month=YYYY-MM`: gasto vs. límite por categoría,
      con bandera `over_budget`
- [x] Meses como texto `"YYYY-MM"` en toda la API (`app/core/dates.py`)
- [x] 15 tests nuevos (48 en total)

## Etapa 4 — Calidad y empaquetado (HECHO)

- [x] `pre-commit` con ruff (`--fix` + `ruff-format`) y hooks basicos (trailing
      whitespace, yaml, archivos grandes). Instalado con `pre-commit install`.
- [x] Cobertura de tests con `pytest-cov`: **96 %** (objetivo era > 85 %)
- [x] `Dockerfile` de la aplicación + `docker-compose` con app + db (con
      healthcheck). **No se pudo probar en esta máquina por no tener Docker
      instalado** — revisar al desplegar.
- [x] Manejo de errores centralizado (handler para excepciones no capturadas,
      responde 500 generico en vez de un stack trace) y logging de cada
      peticion (metodo, ruta, status, duracion)
- [x] Paginación consistente: `/budgets` tambien tiene `skip`/`limit` ahora
- [x] CI: se agrego `ruff format --check` y cobertura con `--cov-report`
- [x] 1 test nuevo (49 en total)

## Etapa 5 — Despliegue (preparado; falta el clic final del usuario)

- [x] `render.yaml` (Blueprint): build, `alembic upgrade head` en el arranque,
      health check, `SECRET_KEY` autogenerada, `DATABASE_URL`/`CORS_ORIGINS` a mano
- [x] Middleware CORS configurable por `CORS_ORIGINS` (para que un frontend pueda llamar)
- [x] La app se niega a arrancar en producción (`DEBUG=false`) si sigue con la
      `SECRET_KEY` de desarrollo
- [x] Endpoint raíz `/` (para que la URL base no sea un 404)
- [x] Badge de CI en el README + guía paso a paso de despliegue (Render + Supabase)
- [x] `conftest.py` en la raíz: fija `SECRET_KEY` de test para que CI/clones sin `.env`
      puedan importar la app
- [x] 6 tests nuevos (55 en total)
- [ ] **Pendiente (lo hace el usuario):** crear proyecto en Supabase, crear el
      Blueprint en Render con las variables, y pegar la URL de la demo en el README

---

### Ideas para practicar más adelante

- Exportar movimientos a CSV
- Soporte multi-moneda con tipo de cambio
- Transacciones recurrentes (suscripciones)
- Rate limiting
- Websocket para notificaciones de presupuesto
