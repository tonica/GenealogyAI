"""Schemas de resposta per a llocs."""

from pydantic import BaseModel, ConfigDict, Field


class PlaceOut(BaseModel):
    """Lloc normalitzat amb les seues coordenades opcionals."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador intern del lloc")
    name: str = Field(description="Nom normalitzat del lloc")
    latitude: float | None = Field(default=None, description="Latitud (WGS84)")
    longitude: float | None = Field(default=None, description="Longitud (WGS84)")
