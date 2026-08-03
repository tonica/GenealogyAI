"""Endpoint d'importació de fitxers GEDCOM."""

import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import get_db
from app.importer import GedcomParseError, parse
from app.schemas.imported import ImportResponse
from app.services.importer import import_gedcom

router = APIRouter()
logger = get_logger("api.import")


@router.post(
    "/import",
    response_model=ImportResponse,
    tags=["import"],
    summary="Importa un fitxer GEDCOM",
    description=(
        "Rep un fitxer .ged (multipart/form-data), el parseja, normalitza "
        "i desa a la base de dades. Retorna estadístiques i problemes "
        "detectats."
    ),
)
async def import_file(
    file: UploadFile = File(..., description="Fitxer GEDCOM a importar"),
    db: Session = Depends(get_db),
) -> dict:
    started = time.perf_counter()
    try:
        raw = await file.read()
    except Exception as exc:  # pragma: no cover - excepció d'E/S
        raise HTTPException(
            status_code=400, detail=f"No es pot llegir el fitxer: {exc}"
        )

    if not raw:
        raise HTTPException(status_code=400, detail="El fitxer està buit")

    try:
        doc = parse(raw)
    except GedcomParseError as exc:
        logger.warning("import parse error file=%s err=%s", file.filename, exc)
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        result = import_gedcom(db, doc)
    except Exception as exc:  # pragma: no cover - errors inesperats del model
        db.rollback()
        logger.error("import failed file=%s err=%s", file.filename, exc)
        raise HTTPException(status_code=500, detail=f"Error d'importació: {exc}")
    db.commit()

    total_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "import ok file=%s persons=%s families=%s issues=%s time_ms=%s",
        file.filename,
        result.persons,
        result.families,
        len(result.issues),
        total_ms,
    )

    return {
        "filename": file.filename or "desconegut.ged",
        "persons": result.persons,
        "families": result.families,
        "sources": result.sources,
        "media": result.media,
        "events": result.events,
        "places": result.places,
        "issues": [iss.__dict__ for iss in result.issues],
        "stats": result.stats.to_dict(),
    }
