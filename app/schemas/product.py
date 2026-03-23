from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


# ============ CATEGORY ============

class CategoryCreate(BaseModel):
    name: str
    slug: str
    type: str  # models, scenes, textures
    parent_id: Optional[UUID] = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    type: str
    parent_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryWithChildren(CategoryOut):
    children: list[CategoryOut] = []


# ============ PRODUCT ============

class ProductCreate(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    type: str  # models, scenes, textures
    category_id: UUID
    brand: Optional[str] = None
    price: float = 0
    style: Optional[str] = None
    materials: list[str] = []
    is_free: bool = False


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    style: Optional[str] = None
    materials: Optional[list[str]] = None
    is_free: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: UUID
    title: str
    slug: str
    description: Optional[str] = None
    type: str
    category_id: UUID
    brand: Optional[str] = None
    price: float
    style: Optional[str] = None
    materials: list[str] = []
    images: list[str] = []
    model_file_url: Optional[str] = None
    model_file_size: Optional[int] = None
    is_free: bool
    is_active: bool
    download_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductList(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
