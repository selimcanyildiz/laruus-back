from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.db.models.product import Product, Category
from app.db.models.user import User
from app.schemas.product import (
    ProductOut, ProductList, CategoryOut, CategoryWithChildren, DownloadOut,
)
from app.services.credit_service import (
    consume_credits, get_today_usage, get_daily_limit,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=list[CategoryWithChildren])
def get_categories(
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Category).filter(Category.parent_id.is_(None))
    if type:
        query = query.filter(Category.type == type)
    return query.all()


@router.get("", response_model=ProductList)
def list_products(
    type: Optional[str] = None,
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    brand: Optional[str] = None,
    style: Optional[str] = None,
    material: Optional[str] = None,
    is_free: Optional[bool] = None,
    search: Optional[str] = None,
    sort: str = "newest",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)

    if type:
        query = query.filter(Product.type == type)
    if brand:
        query = query.filter(Product.brand == brand)
    if style:
        query = query.filter(Product.style == style)
    if is_free is not None:
        query = query.filter(Product.is_free == is_free)
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))
    if material:
        query = query.filter(Product.materials.any(material))

    # Kategori slug ile filtreleme
    if category:
        cat = db.query(Category).filter(Category.slug == category).first()
        if cat:
            if sub_category:
                sub = db.query(Category).filter(
                    Category.slug == sub_category, Category.parent_id == cat.id
                ).first()
                if sub:
                    query = query.filter(Product.category_id == sub.id)
            else:
                # Ana kategori ve alt kategorilerini dahil et
                sub_ids = [c.id for c in db.query(Category).filter(Category.parent_id == cat.id).all()]
                all_ids = [cat.id] + sub_ids
                query = query.filter(Product.category_id.in_(all_ids))

    # Sıralama
    if sort == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort == "credits_asc":
        query = query.order_by(Product.credits.asc())
    elif sort == "credits_desc":
        query = query.order_by(Product.credits.desc())
    elif sort == "popular":
        query = query.order_by(Product.download_count.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ProductList(items=items, total=total, page=page, page_size=page_size)


@router.get("/by-slug/{slug}", response_model=ProductOut)
def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.slug == slug, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/{product_id}/download", response_model=DownloadOut)
def download_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.model_file_url:
        raise HTTPException(status_code=400, detail="No file available for this product")

    charge = 0 if product.is_free else product.credits
    if charge > 0:
        consume_credits(db, current_user.id, charge)

    product.download_count += 1
    db.commit()

    limit = get_daily_limit(db)
    used = get_today_usage(db, current_user.id)
    return DownloadOut(
        download_url=product.model_file_url,
        credits_charged=charge,
        daily_limit=limit,
        used_today=used,
        remaining_today=limit - used,
    )
