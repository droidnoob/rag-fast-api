from fastapi import APIRouter

from app.core.api import route

root_router = APIRouter()
root_router.include_router(route)
