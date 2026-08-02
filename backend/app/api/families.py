"""Endpoints de famílies."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.event import Event
from app.models.family import Family
from app.models.parent_child import ParentChild
from app.schemas.family import FamilyOut
from app.services.serializers import family_out

router = APIRouter()


@router.get(
    "/families",
    response_model=list[FamilyOut],
    tags=["families"],
    summary="Llista de famílies",
    description="Retorna les famílies amb els seus cònjuges i fills.",
)
def list_families(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    stmt = (
        select(Family)
        .options(
            selectinload(Family.father),
            selectinload(Family.mother),
            selectinload(Family.parent_children).selectinload(ParentChild.child),
            selectinload(Family.events).selectinload(Event.place),
        )
        .order_by(Family.id)
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()
    return [family_out(f) for f in rows]


@router.get(
    "/family/{family_id}",
    response_model=FamilyOut,
    tags=["families"],
    summary="Detall d'una família",
)
def get_family(
    family_id: int,
    db: Session = Depends(get_db),
) -> dict:
    stmt = (
        select(Family)
        .where(Family.id == family_id)
        .options(
            selectinload(Family.father),
            selectinload(Family.mother),
            selectinload(Family.parent_children).selectinload(ParentChild.child),
            selectinload(Family.events).selectinload(Event.place),
        )
    )
    fam = db.scalar(stmt)
    if fam is None:
        raise HTTPException(status_code=404, detail="Família no trobada")
    return family_out(fam)
