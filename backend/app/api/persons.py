"""Endpoints de persones."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import PersonRepository
from app.schemas.person import PersonDetail, PersonOut
from app.services.serializers import person_detail, person_out

router = APIRouter()


@router.get(
    "/persons",
    response_model=list[PersonOut],
    tags=["persons"],
    summary="Llista de persones",
    description="Retorna persones, opcionalment filtrades per text i amb paginació.",
)
def list_persons(
    q: str | None = Query(
        default=None, description="Filtra per given_name o surname (substring)"
    ),
    sex: str | None = Query(default=None, description="Filtre M | F | U"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = PersonRepository(db).search(q=q, sex=sex, limit=limit, offset=offset)
    return [person_out(p) for p in rows]


@router.get(
    "/person/{person_id}",
    response_model=PersonDetail,
    tags=["persons"],
    summary="Detall d'una persona",
    description="Retorna les dades, esdeveniments i relacions familiars d'una persona.",
)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
) -> dict:
    person = PersonRepository(db).get_with_detail(person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no trobada")
    return person_detail(person)
