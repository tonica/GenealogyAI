"""Scheme de resposta de l'arbre geneaològic."""

from pydantic import BaseModel, ConfigDict, Field


class TreePerson(BaseModel):
    """Node d'una persona dins de l'arbre."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    xref: str
    given_name: str | None = None
    surname: str | None = None
    birth_year: int | None = Field(default=None, description="Any de naixement")
    death_year: int | None = Field(default=None, description="Any de defunció")
    sex: str | None = None
    parents: list["TreePerson"] = Field(
        default_factory=list, description="Progenitors directes"
    )


class TreeOut(BaseModel):
    """Arbre de descendats d'una persona."""

    model_config = ConfigDict(from_attributes=True)

    root: TreePerson = Field(description="Persona arrel del l'arbre")
    depth: int = Field(description="Profunditat d'ancest que s'ha recorregut")
    person_count: int = Field(description="Nombre de nodes de l'arbre")
