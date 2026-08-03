"""Endpoints de famílies."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import FamilyRepository
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
    fams = FamilyRepository(db).list_with_members(limit=limit, offset=offset)
    return [family_out(f) for f in fams]


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
    fam = FamilyRepository(db).get_with_members(family_id)
    if fam is None:
        raise HTTPException(status_code=404, detail="Família no trobada")
    return family_out(fam)
