"""Schemas de resposta de persones i esdeveniments."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.place import PlaceOut


class EventOut(BaseModel):
    """Un esdeveniment vital associat a una persona o una família."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador de l'esdeveniment")
    event_type: str = Field(description="Tipus (birth, death, marriage, ...)")
    date_text: str | None = Field(default=None, description="Data original GEDCOM")
    date_iso: str | None = Field(default=None, description="Data normalitzada ISO")
    date_year: int | None = Field(default=None, description="Any normalitzat")
    place: PlaceOut | None = Field(default=None, description="Lloc on succeí")


class PersonOut(BaseModel):
    """Resum d'una persona per a llistats."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador intern")
    xref: str = Field(description="Referència GEDCOM (com '@I1@')")
    given_name: str | None = Field(default=None)
    surname: str | None = Field(default=None)
    prefix: str | None = Field(default=None)
    suffix: str | None = Field(default=None)
    sex: str | None = Field(default=None, description="M | F | U")
    birth_date: str | None = Field(default=None)
    death_date: str | None = Field(default=None)


class PersonDetail(PersonOut):
    """Detall complet d'una persona, amb esdeveniments i relacions."""

    notes: str | None = Field(default=None)
    events: list[EventOut] = Field(default_factory=list)
    families_as_child: list[dict] = Field(
        default_factory=list, description="Famílies on la persona és fill/a"
    )
    families_as_spouse: list[dict] = Field(
        default_factory=list, description="Famílies on la persona és cònjuge"
    )
