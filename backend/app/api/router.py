from fastapi import APIRouter
from app.api.v1 import analysis, health

api_router = APIRouter()

# Include version 1 endpoints
api_router.include_router(health.router)
api_router.include_router(analysis.router)
