from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_admin_user
from app.db.models.user import User
from app.db.models.parameter import Parameter
from app.core.parameters import PARAMETER_CATALOG, validate_value
from app.schemas.parameter import ParameterOut, ParameterUpdate

router = APIRouter(prefix="/admin/parameters", tags=["admin-parameters"])


def _build_out(key: str, value: str, updated_at) -> ParameterOut:
    spec = PARAMETER_CATALOG[key]
    return ParameterOut(
        key=key,
        value=value,
        type=spec["type"],
        label=spec["label"],
        description=spec["description"],
        updated_at=updated_at,
        min=spec.get("min"),
        max=spec.get("max"),
    )


@router.get("", response_model=list[ParameterOut])
def list_parameters(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    rows = {p.key: p for p in db.query(Parameter).all()}
    result = []
    for key, spec in PARAMETER_CATALOG.items():
        row = rows.get(key)
        value = row.value if row else str(spec["default"])
        updated_at = row.updated_at if row else None
        result.append(_build_out(key, value, updated_at))
    return result


@router.put("/{key}", response_model=ParameterOut)
def update_parameter(
    key: str,
    data: ParameterUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    if key not in PARAMETER_CATALOG:
        raise HTTPException(status_code=404, detail="Unknown parameter")

    error = validate_value(key, data.value)
    if error:
        raise HTTPException(status_code=400, detail=error)

    row = db.query(Parameter).filter(Parameter.key == key).first()
    if row:
        row.value = data.value
    else:
        row = Parameter(key=key, value=data.value)
        db.add(row)
    db.commit()
    db.refresh(row)

    return _build_out(key, row.value, row.updated_at)
