"""API v1: contracte públic de DTOs per al frontend (Sprint 2).

S'afegeix sense modificar els routers existents (`/api`): el contracte v1
es munta sota `/api/v1` i delega en la capa d'aplicació (`CatalogService`)
i els casos d'ús existents. Mai retorna objectes ORM ni entitats de
domínio: només DTOs.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.application.services.catalog import CatalogService
from app.application.services.quality import (
    DuplicatesUseCase,
    PersonQualityUseCase,
    QualityReportUseCase,
    StatisticsUseCase,
)
from app.application.unit_of_work import UnitOfWork
from app.db.session import get_db
from app.schemas import dto

router = APIRouter()


def _service(db: Session) -> CatalogService:
    return CatalogService(UnitOfWork(db))


# --------------------------------------------------------------------------- #
# Persones
# --------------------------------------------------------------------------- #
@router.get(
    "/persons",
    response_model=list[dto.PersonSummaryDTO],
    tags=["v1"],
    summary="Cerca persones (contracte v1)",
    description=(
        "Filtres: text lliure, nom, cognom, sexe, lloc i any de naixement. "
        "Paginació per limit/offset."
    ),
)
def list_persons(
    q: str | None = Query(default=None, description="Text lliure (nom + cognom)"),
    given_name: str | None = Query(default=None),
    surname: str | None = Query(default=None),
    sex: str | None = Query(default=None, pattern="^[MFU]$"),
    place: str | None = Query(default=None, description="Subcadena del lloc"),
    birth_year: int | None = Query(default=None, description="Any de naixement"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    return _service(db).search(
        q=q,
        given_name=given_name,
        surname=surname,
        sex=sex,
        place=place,
        birth_year=birth_year,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/persons/{person_id}",
    response_model=dto.PersonDetailsDTO,
    tags=["v1"],
    summary="Detall d'una persona (contracte v1)",
    description=(
        "Resum + relacions (pares, cònjuges, fills), línia del temps, "
        "qualitat, possibles duplicats i tasques de recerca."
    ),
)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return _service(db).person(person_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# --------------------------------------------------------------------------- #
# Famílies
# --------------------------------------------------------------------------- #
@router.get(
    "/families",
    response_model=list[dto.FamilyDTO],
    tags=["v1"],
    summary="Llista de famílies (contracte v1)",
)
def list_families(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[dict]:
    return _service(db).families(limit=limit, offset=offset)


@router.get(
    "/families/{family_id}",
    response_model=dto.FamilyDTO,
    tags=["v1"],
    summary="Detall d'una família (contracte v1)",
)
def get_family(
    family_id: int,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return _service(db).family(family_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# --------------------------------------------------------------------------- #
# Intel·ligència i qualitat
# --------------------------------------------------------------------------- #
@router.get(
    "/statistics",
    response_model=dto.StatisticsDTO,
    tags=["v1"],
    summary="Estadístiques del conjunt de dades (contracte v1)",
)
def statistics(db: Session = Depends(get_db)) -> dict:
    return StatisticsUseCase(UnitOfWork(db)).execute().to_dict()


@router.get(
    "/quality/report",
    response_model=dto.QualityReportDTO,
    tags=["v1"],
    summary="Informe de qualitat de dades (contracte v1)",
)
def quality_report(db: Session = Depends(get_db)) -> dict:
    return QualityReportUseCase(UnitOfWork(db)).execute().to_dict()


@router.get(
    "/quality/persons/{person_id}",
    response_model=dto.PersonQualityDTO,
    tags=["v1"],
    summary="Qualitat individual d'una persona (contracte v1)",
)
def person_quality(
    person_id: int,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return PersonQualityUseCase(UnitOfWork(db)).execute(person_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/duplicates",
    response_model=list[dto.DuplicateCandidateDTO],
    tags=["v1"],
    summary="Possibles persones duplicades (contracte v1)",
)
def duplicates(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    candidates = DuplicatesUseCase(UnitOfWork(db)).execute()
    return [c.to_dict() for c in candidates[:limit]]


@router.get(
    "/research/tasks",
    response_model=list[dto.ResearchTaskDTO],
    tags=["v1"],
    summary="Tasques de recerca suggerides (contracte v1)",
)
def research_tasks(
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[dict]:
    return _service(db).research_tasks(limit=limit)


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
@router.get(
    "/dashboard",
    response_model=dto.DashboardDTO,
    tags=["v1"],
    summary="Resum per a la pàgina d'inici (contracte v1)",
)
def dashboard(db: Session = Depends(get_db)) -> dict:
    return _service(db).dashboard()
