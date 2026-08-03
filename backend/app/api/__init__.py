"""Rutes de la API. S'agreguen els routers de domini."""

from fastapi import APIRouter

from app.api import (
    families,
    import_,
    persons,
    places,
    quality,
    routes,
    trees,
)

api_router = APIRouter()
api_router.include_router(routes.router)
api_router.include_router(persons.router)
api_router.include_router(families.router)
api_router.include_router(places.router)
api_router.include_router(trees.router)
api_router.include_router(import_.router)
api_router.include_router(quality.router)
