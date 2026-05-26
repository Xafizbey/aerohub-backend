from fastapi import APIRouter

from app.api.v1.endpoints import auth, movies, music, analytics, cafe, settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(movies.router)
api_router.include_router(music.router)
api_router.include_router(analytics.router)
api_router.include_router(cafe.router)
api_router.include_router(settings.router)
