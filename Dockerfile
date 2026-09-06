# Imagen liviana de Python (sin las herramientas de compilacion que trae la
# imagen completa; alcanza porque nuestras dependencias no compilan nada).
FROM python:3.12-slim

WORKDIR /app

# Se copia solo lo que el paquete necesita para instalarse y correr (no
# tests, no .venv, no .git): imagen mas chica y build mas rapido.
COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
