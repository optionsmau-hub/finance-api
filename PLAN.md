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

## Etapa 3 — Presupuestos y reportes

- [ ] Modelo `Budget`: límite mensual por categoría
- [ ] `GET /api/v1/reports/summary?month=YYYY-MM`: total ingresos, gastos, balance
- [ ] `GET /api/v1/reports/by-category`: gasto agrupado por categoría
- [ ] Alerta cuando el gasto supera el presupuesto

## Etapa 4 — Calidad y empaquetado

- [ ] `pre-commit` con ruff (formato + lint automáticos)
- [ ] Cobertura de tests con `pytest-cov` (objetivo: > 85 %)
- [ ] `Dockerfile` de la aplicación + `docker-compose` con app + db
- [ ] Manejo de errores centralizado y logging
- [ ] Paginación consistente en todos los listados

## Etapa 5 — Despliegue

- [ ] Desplegar en Render / Railway / Fly.io (capa gratuita)
- [ ] Variables de entorno de producción
- [ ] Badge de CI y enlace a la demo en el README

---

### Ideas para practicar más adelante

- Exportar movimientos a CSV
- Soporte multi-moneda con tipo de cambio
- Transacciones recurrentes (suscripciones)
- Rate limiting
- Websocket para notificaciones de presupuesto
