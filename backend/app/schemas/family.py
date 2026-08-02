"""Schema de resposta de famílies."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import EventOut, PersonOut


class FamilyOut(BaseModel):
    """Representació d'una família i els seus integrants."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador intern de la família")
    xref: str | None = Field(default=None, description="Referència GEDCOM")
    father: PersonOut | None = Field(default=None, description="Cònjuge/doc vostre")
    mother: PersonOut | None = Field(default=None, description="Cònjuge/filla")
    children: list[PersonOut] = Field(
        default_factory=list, description="Fills ordenats per ordre de naixement"
    )
    marriage_date: str | None = Field(default=None)
    marriage_place: str | None = Field(default=None)
    events: list[EventOut] = Field(default_factory=list)
