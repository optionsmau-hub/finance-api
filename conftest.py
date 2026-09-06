"""Configuracion global de pytest (raiz del repo).

pytest carga este archivo antes que cualquier test o que tests/conftest.py.
Lo usamos para preparar el entorno ANTES de que se importe la aplicacion.
"""

import os

# Sin un archivo .env (por ejemplo en CI), la configuracion exige una
# SECRET_KEY propia cuando debug=false. Aqui ponemos una de prueba para que
# los tests puedan importar la app sin fallar en el arranque.
os.environ.setdefault("SECRET_KEY", "testing-secret-key-not-for-production-0123456789")
