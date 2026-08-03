"""Endpoint de l'arbre geneaològic."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import PersonRepository
from app.schemas.tree import TreeOut
from app.services.tree import build_tree

router = APIRouter()


@router.get(
    "/tree/{person_id}",
    response_model=TreeOut,
    tags=["tree"],
    summary="Arbre de progenitors d'una persona",
    description="Retorna els ascendents (pares/avis/...) fins a `depth` generacions.",
)
def get_tree(
    person_id: int,
    depth: int = Query(default=3, ge=1, le=6, description="Generacions a recórrer"),
    db: Session = Depends(get_db),
) -> dict:
    person = PersonRepository(db).get_with_detail(person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no trobada")
    return build_tree(person, max_depth=depth)
