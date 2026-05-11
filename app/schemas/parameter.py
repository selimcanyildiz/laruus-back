from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class ParameterOut(BaseModel):
    key: str
    value: str
    type: str
    label: str
    description: str
    updated_at: Optional[datetime] = None
    # CATALOG'dan ek metadata (varsa)
    min: Optional[Any] = None
    max: Optional[Any] = None


class ParameterUpdate(BaseModel):
    value: str
