from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.api.deps import get_db, get_admin_user
from app.db.models.user import User
from app.db.models.product import Product, Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductOut,
    CategoryCreate, CategoryOut, CategoryWithChildren,
)
from app.services.s3_service import upload_file, delete_file

router = APIRouter(prefix="/admin", tags=["admin"])


# ============ CATEGORIES ============

@router.post("/categories", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/categories", response_model=list[CategoryWithChildren])
def list_categories(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    query = db.query(Category).filter(Category.parent_id.is_(None))
    if type:
        query = query.filter(Category.type == type)
    return query.all()


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted"}


# ============ PRODUCTS ============

@router.get("/products", response_model=list[ProductOut])
def list_products(
    type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    query = db.query(Product)
    if type:
        query = query.filter(Product.type == type)
    return query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


@router.post("/products", response_model=ProductOut)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}")
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # S3'ten dosyaları sil
    for img_url in (product.images or []):
        key = img_url.split(".amazonaws.com/")[-1] if ".amazonaws.com/" in img_url else None
        if key:
            try:
                delete_file(key)
            except Exception:
                pass

    if product.model_file_url:
        key = product.model_file_url.split(".amazonaws.com/")[-1] if ".amazonaws.com/" in product.model_file_url else None
        if key:
            try:
                delete_file(key)
            except Exception:
                pass

    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}


# ============ FILE UPLOADS ============

@router.post("/products/{product_id}/images")
def upload_product_images(
    product_id: UUID,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    uploaded_urls = []
    for f in files:
        result = upload_file(f.file, folder=f"products/{product_id}/images", filename=f.filename)
        uploaded_urls.append(result["url"])

    current_images = product.images or []
    product.images = current_images + uploaded_urls
    db.commit()
    db.refresh(product)
    return {"images": product.images}


@router.post("/products/{product_id}/model-file")
def upload_model_file(
    product_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = upload_file(file.file, folder=f"products/{product_id}/model", filename=file.filename)
    product.model_file_url = result["url"]
    product.model_file_size = file.size
    db.commit()
    db.refresh(product)
    return {"model_file_url": product.model_file_url, "model_file_size": product.model_file_size}
