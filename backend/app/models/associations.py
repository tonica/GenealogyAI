from sqlalchemy import Column, ForeignKey, Table

from app.db.session import Base

# Taules d'associacion molts-a-molts entre fonts i entitats genealogiques.
person_sources = Table(
    "person_sources",
    Base.metadata,
    Column(
        "person_id",
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "source_id",
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

event_sources = Table(
    "event_sources",
    Base.metadata,
    Column(
        "event_id",
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "source_id",
        ForeignKey("sources.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
