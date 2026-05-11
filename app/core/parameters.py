"""
Sistem parametreleri.

Her parametre `PARAMETER_CATALOG` içinde tanımlanır. Admin paneli sadece
buradaki key'lerin değerlerini güncelleyebilir; yeni key UI'dan eklenemez.

Yeni bir parametre eklemek için:
  1) CATALOG'a satır ekle (default, type, label, description, optional min/max)
  2) Frontend AdminParameters sayfası onu otomatik gösterir
  3) Uygulamadaki tüketici tarafı `get_int(db, "yeni_key")` ile okur
"""

from typing import Any, Optional
from sqlalchemy.orm import Session

from app.db.models.parameter import Parameter


PARAMETER_CATALOG: dict[str, dict[str, Any]] = {
    "daily_credit_limit": {
        "default": "100",
        "type": "int",
        "label": "Günlük Kredi Limiti",
        "description": "Bir kullanıcının günde harcayabileceği maksimum kredi.",
        "min": 0,
    },
}


def _coerce(value: str, value_type: str) -> Any:
    if value_type == "int":
        return int(value)
    if value_type == "bool":
        return value.lower() in ("1", "true", "yes", "on")
    return value


def validate_value(key: str, value: str) -> Optional[str]:
    """None dönerse OK; string dönerse hata mesajı."""
    spec = PARAMETER_CATALOG.get(key)
    if spec is None:
        return "Unknown parameter"

    try:
        coerced = _coerce(value, spec["type"])
    except (TypeError, ValueError):
        return f"Value must be of type {spec['type']}"

    if spec["type"] == "int":
        if "min" in spec and coerced < spec["min"]:
            return f"Value must be ≥ {spec['min']}"
        if "max" in spec and coerced > spec["max"]:
            return f"Value must be ≤ {spec['max']}"

    return None


def seed_parameters(db: Session) -> None:
    """CATALOG'da olup DB'de olmayan parametrelerin default değerlerini yazar."""
    existing = {p.key for p in db.query(Parameter).all()}
    added = False
    for key, spec in PARAMETER_CATALOG.items():
        if key not in existing:
            db.add(Parameter(key=key, value=str(spec["default"])))
            added = True
    if added:
        db.commit()


def get_raw(db: Session, key: str) -> str:
    """Ham string değer döner. CATALOG'da yoksa default'a düşer; o da yoksa KeyError."""
    row = db.query(Parameter).filter(Parameter.key == key).first()
    if row:
        return row.value
    spec = PARAMETER_CATALOG.get(key)
    if spec is None:
        raise KeyError(f"Unknown parameter: {key}")
    return str(spec["default"])


def get_int(db: Session, key: str) -> int:
    return int(get_raw(db, key))


def get_bool(db: Session, key: str) -> bool:
    return get_raw(db, key).lower() in ("1", "true", "yes", "on")
