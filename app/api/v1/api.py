from fastapi import APIRouter
from app.api.v1 import auth, users, products, admin, parameters

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(admin.router)
api_router.include_router(parameters.router)
