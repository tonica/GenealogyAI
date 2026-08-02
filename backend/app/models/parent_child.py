from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.family import Family
    from app.models.person import Person


class ParentChild(TimestampMixin, Base):
    """Associacio entre un familial, un fill i (opcionalment) un dels pares."""

    __tablename__ = "parent_children"
    __table_args__ = (
        Index("ix_parent_child_family", "family_id"),
        Index("ix_parent_child_child", "child_id"),
        Index("ix_parent_child_parent", "parent_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE")
    )
    child_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE")
    )
    role: Mapped[Optional[str]] = mapped_column(String(20), comment="father | mother")
    sibling_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # --- Relacions ---
    family: Mapped[Family] = relationship(back_populates="parent_children")
    child: Mapped[Person] = relationship(
        back_populates="child_links",
        foreign_keys=[child_id],
        post_update=True,
    )
    parent: Mapped[Optional[Person]] = relationship(
        back_populates="parent_links",
        foreign_keys=[parent_id],
        post_update=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ParentChild id={self.id} family={self.family_id} "
            f"child={self.child_id}>"
        )
