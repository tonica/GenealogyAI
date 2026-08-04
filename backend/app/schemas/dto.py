"""DTOs del contracte públic de la API v1 (Sprint 2).

Defineixen la forma que el frontend consumeix. La capa API mai retorna
objectes ORM ni entitats de domínio: només aquests DTOs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Persones
# --------------------------------------------------------------------------- #
class PersonSummaryDTO(BaseModel):
    """Resum d'una persona per a llistats i cerques."""

    id: int = Field(description="Identificador intern")
    xref: str | None = Field(default=None, description="Referència GEDCOM")
    given_name: str | None = Field(default=None)
    surname: str | None = Field(default=None)
    prefix: str | None = Field(default=None)
    suffix: str | None = Field(default=None)
    sex: str | None = Field(default=None, description="M | F | U")
    display_name: str = Field(description="Nom complet llegible")
    birth_date: str | None = Field(default=None)
    death_date: str | None = Field(default=None)
    birth_year: int | None = Field(default=None)
    death_year: int | None = Field(default=None)
    birth_place: str | None = Field(default=None)
    death_place: str | None = Field(default=None)
    quality: float | None = Field(default=None, description="Puntuació 0..1")


class TimelineEventDTO(BaseModel):
    """Esdeveniment vital de la línia del temps d'una persona."""

    id: int | None = Field(default=None)
    event_type: str | None = Field(default=None)
    date_text: str | None = Field(default=None)
    date_iso: str | None = Field(default=None)
    date_year: int | None = Field(default=None)
    place: str | None = Field(default=None, description="Nom del lloc")
    place_id: int | None = Field(default=None)
    description: str | None = Field(default=None)
    sort_year: int | None = Field(default=None, description="Any d'ordenació")


class QualityFactorDTO(BaseModel):
    """Factor explicable de la puntuació de qualitat."""

    name: str
    contribution: float
    weight: float
    reason: str
    direction: str


class PersonQualityDTO(BaseModel):
    """Puntuació de qualitat d'una persona amb desglossament."""

    person_id: int | None = None
    xref: str | None = None
    score: float
    missing: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    factors: list[QualityFactorDTO] = Field(default_factory=list)


class SpouseDTO(BaseModel):
    """Cònjuge i família pròpia d'una persona."""

    family_id: int
    spouse: "PersonSummaryDTO | None" = None
    marriage_date: str | None = None
    marriage_place: str | None = None


class DuplicatePersonDTO(BaseModel):
    """Referència a una persona dins d'un candidat a duplicat."""

    id: int | None = None
    xref: str | None = None
    name: str = ""


class DuplicateCandidateDTO(BaseModel):
    """Parell de persones que poden ser la mateixa."""

    person_a: DuplicatePersonDTO
    person_b: DuplicatePersonDTO
    score: float
    confidence: float
    rules_used: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class ResearchTaskDTO(BaseModel):
    """Tasca de recerca suggerida."""

    person_id: int | None = None
    xref: str | None = None
    objective: str
    kind: str
    hypothesis: str | None = None
    related_person_ids: list[int] = Field(default_factory=list)


class PersonDetailsDTO(PersonSummaryDTO):
    """Detall complet d'una persona (resum + relacions + intel·ligència)."""

    notes: str | None = Field(default=None)
    birth: "TimelineEventDTO | None" = Field(default=None)
    death: "TimelineEventDTO | None" = Field(default=None)
    parents: list[PersonSummaryDTO] = Field(default_factory=list)
    spouses: list[SpouseDTO] = Field(default_factory=list)
    children: list[PersonSummaryDTO] = Field(default_factory=list)
    events: list[TimelineEventDTO] = Field(default_factory=list)
    timeline: list[TimelineEventDTO] = Field(default_factory=list)
    quality_detail: "PersonQualityDTO | None" = Field(default=None)
    duplicates: list[DuplicateCandidateDTO] = Field(default_factory=list)
    tasks: list[ResearchTaskDTO] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Famílies
# --------------------------------------------------------------------------- #
class FamilyDTO(BaseModel):
    """Família amb els seus integrants."""

    id: int = Field(description="Identificador intern")
    xref: str | None = Field(default=None, description="Referència GEDCOM")
    father: "PersonSummaryDTO | None" = Field(default=None)
    mother: "PersonSummaryDTO | None" = Field(default=None)
    children: list[PersonSummaryDTO] = Field(
        default_factory=list, description="Fills ordenats per naixement"
    )
    marriage_date: str | None = Field(default=None)
    marriage_place: str | None = Field(default=None)
    events: list[TimelineEventDTO] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Estadístiques
# --------------------------------------------------------------------------- #
class StatisticsDTO(BaseModel):
    """Estadístiques agregades del conjunt de dades."""

    persons: int = 0
    families: int = 0
    sources: int = 0
    media: int = 0
    events: int = 0
    males: int = 0
    females: int = 0
    average_age: float | None = None
    max_age: int | None = None
    events_by_type: dict[str, int] = Field(default_factory=dict)
    sex_by: dict[str, int] = Field(default_factory=dict)
    surname_frequency: dict[str, int] = Field(default_factory=dict)
    persons_without_name: int = 0
    persons_without_data: int = 0
    birth_year_range: list[int | None] = Field(default_factory=lambda: [None, None])
    births_by_year: dict[int, int] = Field(default_factory=dict)
    deaths_by_year: dict[int, int] = Field(default_factory=dict)
    top_places: list[dict] = Field(default_factory=list)
    top_surnames: list[dict] = Field(default_factory=list)
    largest_branches: list[int] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Qualitat
# --------------------------------------------------------------------------- #
class QualityFindingDTO(BaseModel):
    """Una observació de qualitat de dades."""

    category: str
    severity: str  # error | warning | info
    message: str
    ref: str | None = None
    metadata: dict = Field(default_factory=dict)


class QualityReportDTO(BaseModel):
    """Informe complet de qualitat de dades."""

    total: int = 0
    errors: list[QualityFindingDTO] = Field(default_factory=list)
    warnings: list[QualityFindingDTO] = Field(default_factory=list)
    infos: list[QualityFindingDTO] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Dashboard
# --------------------------------------------------------------------------- #
class DashboardDTO(BaseModel):
    """Resum per a la pàgina d'inici."""

    persons: int = 0
    families: int = 0
    events: int = 0
    places: int = 0
    sources: int = 0
    media: int = 0
    males: int = 0
    females: int = 0
    average_age: float | None = None
    average_quality: float | None = None
    duplicates: int = 0
    pending_tasks: int = 0
    last_import: str | None = Field(
        default=None, description="Data (ISO) de la darrera importació"
    )
