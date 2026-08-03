"""Endpoints de llocs."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import PlaceRepository
from app.schemas.place import PlaceOut

router = APIRouter()


@router.get(
    "/places",
    response_model=list[PlaceOut],
    tags=["places"],
    summary="Llista de llocs",
    description="Retorna tots els llocs normalitzats, opcionalment filtrats.",
)
def list_places(
    q: str | None = Query(default=None, description="Filtra pel nom del lloc"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list:
    return PlaceRepository(db).list(q=q, limit=limit, offset=offset)
