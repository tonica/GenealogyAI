"""Endpoints de persones."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.event import Event
from app.models.parent_child import ParentChild
from app.models.person import Person
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
    stmt = select(Person)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(Person.given_name.ilike(like), Person.surname.ilike(like))
        )
    if sex:
        stmt = stmt.where(Person.sex == sex)
    stmt = stmt.order_by(Person.surname, Person.given_name).limit(limit).offset(offset)
    rows = db.scalars(stmt).all()
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
    stmt = (
        select(Person)
        .where(Person.id == person_id)
        .options(
            selectinload(Person.events).selectinload(Event.place),
            selectinload(Person.families_as_father),
            selectinload(Person.families_as_mother),
            selectinload(Person.child_links).selectinload(ParentChild.family),
        )
    )
    person = db.scalar(stmt)
    if person is None:
        raise HTTPException(status_code=404, detail="Persona no trobada")
    return person_detail(person)
