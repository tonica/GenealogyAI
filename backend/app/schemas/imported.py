"""Schemes de resposta de la importació."""

from pydantic import BaseModel, ConfigDict, Field


class ImportIssueOut(BaseModel):
    """Un problema detectat durant la importació."""

    model_config = ConfigDict(from_attributes=True)

    level: str = Field(description="error | warning")
    code: str
    xref: str
    message: str


class ImportStatOut(BaseModel):
    """Estadístiques de l'importació."""

    model_config = ConfigDict(from_attributes=True)

    persons: int = Field(default=0)
    families: int = Field(default=0)
    sources: int = Field(default=0)
    media: int = Field(default=0)
    places: int = Field(default=0)
    notes: int = Field(default=0)
    events: int = Field(default=0)
    events_by_type: dict[str, int] = Field(default_factory=dict)
    sex_by: dict[str, int] = Field(default_factory=dict)
    persons_with_birth: int = Field(default=0)
    persons_with_death: int = Field(default=0)
    persons_without_name: int = Field(default=0)
    surname_frequency: dict[str, int] = Field(default_factory=dict)
    birth_year_range: list[int | None] = Field(default_factory=lambda: [None, None])
    unresolved_refs: int = Field(default=0)


class ImportResponse(BaseModel):
    """Resposta de l'operació d'importació d'un fitxer GEDCOM."""

    model_config = ConfigDict(from_attributes=True)

    filename: str = Field(description="Nom del fitxer rebut")
    persons: int = Field(default=0)
    families: int = Field(default=0)
    sources: int = Field(default=0)
    media: int = Field(default=0)
    events: int = Field(default=0)
    places: int = Field(default=0)
    issues: list[ImportIssueOut] = Field(default_factory=list)
    stats: ImportStatOut = Field(default_factory=ImportStatOut)
