"""Endpoint de l'arbre geneaològic."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.parent_child import ParentChild
from app.models.person import Person
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
    stmt = (
        select(Person)
        .where(Person.id == person_id)
        .options(
            selectinload(Person.events),
            selectinload(Person.child_links).selectinload(ParentChild.family),
        )
    )
    person = db.scalar(stmt)
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no trobada")
    return build_tree(person, max_depth=depth)
