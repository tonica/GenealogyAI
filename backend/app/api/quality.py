"""Endpoints de qualitat de dades i intel·ligència genealògica.

Afegits a l'Sprint 1.6. Només llegeixen i analitzen dades (no modifiquen
la BDD). Delegen l'anàlisi als casos d'ús de l'application layer.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.application.services.quality import (
    DuplicatesUseCase,
    PersonQualityUseCase,
    QualityReportUseCase,
    ResearchTasksUseCase,
    StatisticsUseCase,
)
from app.application.unit_of_work import UnitOfWork
from app.db.session import get_db

router = APIRouter()


@router.get(
    "/quality/report",
    tags=["quality"],
    summary="Informe de qualitat de dades",
    description="Retorna observacions de qualitat (dates impossibles, cronologia, "
    "duplicats, relacions, topònims i variants de nom) en format JSON.",
)
def quality_report(
    format: str = Query(
        default="json", pattern="^(json|markdown)$", description="Sortida json|markdown"
    ),
    db: Session = Depends(get_db),
):
    report = QualityReportUseCase(UnitOfWork(db)).execute()
    if format == "markdown":
        return {"report": report.to_markdown()}
    return report.to_dict()


@router.get(
    "/quality/person/{person_id}",
    tags=["quality"],
    summary="Qualitat individual d'una persona",
    description="Score de qualitat (0..1) amb factors explicables i mancances.",
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
    tags=["quality"],
    summary="Possibles persones duplicades",
    description="Candidats a duplicats ordenats per puntuació (més alta primer).",
)
def duplicates(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    candidates = DuplicatesUseCase(UnitOfWork(db)).execute()
    return [c.to_dict() for c in candidates[:limit]]


@router.get(
    "/statistics",
    tags=["quality"],
    summary="Estadístiques del conjunt de dades",
    description="Agregats demogràfics i genealògics (edats, naixements/defuncions "
    "per any, cognoms i llocs principals, branques).",
)
def statistics(db: Session = Depends(get_db)) -> dict:
    return StatisticsUseCase(UnitOfWork(db)).execute().to_dict()


@router.get(
    "/research/tasks",
    tags=["quality"],
    summary="Tasques de recerca suggerides",
    description="Suggereix recerques (baptisme, matrimoni, defunció, pares, "
    "duplicats) a partir de les mancances de dades.",
)
def research_tasks(
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[dict]:
    tasks = ResearchTasksUseCase(UnitOfWork(db)).execute()
    return [t.to_dict() for t in tasks[:limit]]
