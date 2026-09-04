"""Utilidades para trabajar con periodos mensuales.

Un mes se representa como texto "YYYY-MM" (ej. "2026-09") en toda la API:
es mas facil de escribir en una URL que dos fechas.
"""

from calendar import monthrange
from datetime import date

MONTH_PATTERN = r"^\d{4}-(0[1-9]|1[0-2])$"


def month_bounds(month: str) -> tuple[date, date]:
    """Dado "2026-09", devuelve (primer dia, ultimo dia) de ese mes."""
    year_str, month_str = month.split("-")
    year, mon = int(year_str), int(month_str)
    first_day = date(year, mon, 1)
    last_day = date(year, mon, monthrange(year, mon)[1])
    return first_day, last_day
