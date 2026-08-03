"""Regles de duplicació: cada regla avalua una parella de `Person`.

Arquitectura: DuplicateDetector -> Rules -> Score -> Decision.
Cada regla retorna `RuleResult` amb score (0..1), reason i confidence.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.entities import Person
from app.domain.services.date_engine import DateEngine
from app.domain.value_objects import PersonName


@dataclass
class RuleResult:
    """Resultat d'una regla de duplicació."""

    score: float  # 0..1 (1 = coincidència forta)
    reason: str
    confidence: float  # 0..1


class DuplicateRule(ABC):
    """Base de les regles de duplicació."""

    name: str = "rule"

    @abstractmethod
    def evaluate(self, a: Person, b: Person) -> RuleResult: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


# ------------------------------------------------------------------ regles


class NameRule(DuplicateRule):
    """Coincidència de nom: fonètica + edició."""

    name = "name"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        an = PersonName(given=a.given_name, surnames=a.surname)
        bn = PersonName(given=b.given_name, surnames=b.surname)
        if not an.full_name and not bn.full_name:
            return RuleResult(0.0, "cap nom", 0.0)

        given_sim = 0.0
        if a.given_name and b.given_name:
            given_sim = PersonName(given=a.given_name).similarity(
                PersonName(given=b.given_name)
            )
        surname_sim = 0.0
        if a.surname and b.surname:
            surname_sim = PersonName(given=a.surname).similarity(
                PersonName(given=b.surname)
            )

        score = 0.6 * max(given_sim, surname_sim) + 0.4 * min(
            given_sim if a.given_name else surname_sim,
            surname_sim if a.surname else given_sim,
        )
        if not a.given_name and not a.surname:
            score = 0.0
        confidence = max(given_sim, surname_sim)
        return RuleResult(round(score, 2), "noms similars", round(confidence, 2))


class BirthRule(DuplicateRule):
    """Coincidència de data de naixement."""

    name = "birth"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        if not a.birth_date or not b.birth_date:
            return RuleResult(0.0, "sense data de naixement", 0.0)
        d = DateEngine()
        da, db = d.parse(a.birth_date), d.parse(b.birth_date)
        if not da.valid or not db.valid:
            return RuleResult(0.0, "dates no vàlides", 0.0)
        # Tolerància: mateix any, o un rang que contingui l'altre.
        if da.year == db.year:
            return RuleResult(1.0, "mateix any de naixement", 0.9)
        if da.overlaps(db):
            return RuleResult(0.8, "períodes de naixement solapats", 0.7)
        if abs(da.year - db.year) <= 1:
            return RuleResult(0.5, "anys propers", 0.5)
        return RuleResult(0.0, "anys diferents", 0.9)


class DeathRule(DuplicateRule):
    """Coincidència de data de defunció."""

    name = "death"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        if not a.death_date or not b.death_date:
            return RuleResult(0.0, "sense data de defunció", 0.0)
        d = DateEngine()
        da, db = d.parse(a.death_date), d.parse(b.death_date)
        if not da.valid or not db.valid:
            return RuleResult(0.0, "dates no vàlides", 0.0)
        if da.year == db.year:
            return RuleResult(1.0, "mateix any de defunció", 0.9)
        if abs(da.year - db.year) <= 1:
            return RuleResult(0.5, "anys propers", 0.5)
        return RuleResult(0.0, "anys diferents", 0.9)


class ParentsRule(DuplicateRule):
    """Coincidència de pares (per xref o per família)."""

    name = "parents"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        a_fams = set(a.family_as_child_ids)
        b_fams = set(b.family_as_child_ids)
        if not a_fams or not b_fams:
            return RuleResult(0.0, "sense famílies com a fill", 0.0)
        inter = a_fams & b_fams
        if inter:
            return RuleResult(1.0, f"mateixes famílies paternals {inter}", 0.95)
        return RuleResult(0.2, "famílies paternals diferents", 0.4)


class MarriageRule(DuplicateRule):
    """Coincidència de cònjuge (per famílies com a cònjuge)."""

    name = "marriage"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        a_fams = set(a.family_as_spouse_ids)
        b_fams = set(b.family_as_spouse_ids)
        if not a_fams or not b_fams:
            return RuleResult(0.0, "sense famílies com a cònjuge", 0.0)
        inter = a_fams & b_fams
        if inter:
            return RuleResult(1.0, f"mateix matrimoni {inter}", 0.9)
        return RuleResult(0.15, "matrimonis diferents", 0.3)


class ChildrenRule(DuplicateRule):
    """Coincidència de fills (per llistes d'ids de fills de les famílies)."""

    name = "children"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        if not hasattr(a, "_children_ids") or not hasattr(b, "_children_ids"):
            return RuleResult(0.0, "sense dades de fills", 0.0)
        a_ids = set(getattr(a, "_children_ids", []) or [])
        b_ids = set(getattr(b, "_children_ids", []) or [])
        if not a_ids or not b_ids:
            return RuleResult(0.0, "sense fills", 0.0)
        inter = a_ids & b_ids
        union = a_ids | b_ids
        score = len(inter) / len(union) if union else 0.0
        if score > 0:
            return RuleResult(
                round(score, 2), f"fills en comú: {len(inter)}", round(score, 2)
            )
        return RuleResult(0.1, "fills diferents", 0.3)


class PlaceRule(DuplicateRule):
    """Coincidència de lloc de naixement (si està als atributs)."""

    name = "place"

    def evaluate(self, a: Person, b: Person) -> RuleResult:
        ap = getattr(a, "birth_place", None)
        bp = getattr(b, "birth_place", None)
        if not ap or not bp:
            return RuleResult(0.0, "sense lloc de naixement", 0.0)
        if _norm(ap) == _norm(bp):
            return RuleResult(1.0, "mateix lloc de naixement", 0.9)
        if _norm(ap) in _norm(bp) or _norm(bp) in _norm(ap):
            return RuleResult(0.7, "llocs relacionats", 0.6)
        return RuleResult(0.0, "llocs diferents", 0.7)


def _norm(value: str) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()
