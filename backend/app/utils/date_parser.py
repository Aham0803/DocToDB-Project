from datetime import datetime, date
from typing import Optional

def parse_date_safe(d, default_today: bool = False) -> Optional[date]:
    """Safely converts string/date/datetime to datetime.date object for SQLite and MySQL compatibility."""
    if not d:
        return date.today() if default_today else None
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    clean = str(d).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(clean).date()
    except Exception:
        return date.today() if default_today else None
