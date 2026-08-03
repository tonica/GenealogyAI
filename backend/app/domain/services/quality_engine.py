"""Servei de domínio `QualityEngine`.

Calcula una puntuació de qualitat per persona basada en factors
explicables (naixement, defunció, pares, fills, llocs, fonts, cronologia,
relacions). Cada factor diu si suma o resta i per què. No escriu a BD.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Person
from app.domain.services.date_engine import DateEngine


@dataclass
class QualityFactor:
    """Factor individual de qualitat amb la seva justificació."""

    name: str
    contribution: float  # pot ser positiva (suma) o negativa (resta)
    weight: float
    reason: str
    direction: str = "add"  # "add" | "subtract"


@dataclass
class PersonQuality:
    """Qualitat d'una persona individual amb desglossament."""

    person_id: int | None = None
    xref: str | None = None
    score: float = 0.0
    missing: list[str] = field(default_factory=list)
    factors: list[QualityFactor] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def factor(self, name: str) -> QualityFactor | None:
        for f in self.factors:
            if f.name == name:
                return f
        return None

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "xref": self.xref,
            "score": self.score,
            "missing": list(self.missing),
            "issues": list(self.issues),
            "factors": [
                {
                    "name": f.name,
                    "contribution": f.contribution,
                    "weight": f.weight,
                    "reason": f.reason,
                    "direction": f.direction,
                }
                for f in self.factors
            ],
        }


@dataclass
class QualityReport:
    """Informe global de qualitat d'un conjunt de persones."""

    average_score: float = 0.0
    evaluations: list[PersonQuality] = field(default_factory=list)

    @property
    def best(self) -> PersonQuality | None:
        if not self.evaluations:
            return None
        return max(self.evaluations, key=lambda q: q.score)

    @property
    def distribution(self) -> dict[str, int]:
        """Distribució de qualitat (excel·lent/bona/regular/baixa)."""
        buckets = {"excellent": 0, "good": 0, "regular": 0, "low": 0}
        for q in self.evaluations:
            if q.score >= 0.8:
                buckets["excellent"] += 1
            elif q.score >= 0.6:
                buckets["good"] += 1
            elif q.score >= 0.4:
                buckets["regular"] += 1
            else:
                buckets["low"] += 1
        return buckets

    def to_dict(self) -> dict:
        return {
            "average_score": self.average_score,
            "distribution": self.distribution,
            "evaluations": [q.to_dict() for q in self.evaluations],
        }


class QualityEngine:
    """Motor de qualitat basat en factors explicables.

    El rang de la puntuació és 0..1; els factors amb `direction="subtract"`
    resten (cronologia impossible, etc.).
    """

    def evaluate_person(
        self,
        person: Person,
        *,
        has_parents: bool = False,
        has_children: bool = False,
        has_sources: bool = False,
        event_count: int = 0,
        place_count: int = 0,
        has_chronology_issue: bool = False,
    ) -> PersonQuality:
        factors: list[QualityFactor] = []
        issues: list[str] = []
        missing: list[str] = []

        self._add_basic_factors(person, factors, missing)
        self._add_relationships_factors(factors, has_parents, has_children, missing)
        self._add_sources_factors(
            factors, has_sources, event_count, place_count, missing
        )
        self._add_chronology(person, factors, issues, has_chronology_issue)

        # Càlcul de la puntuació: suma ponderada dels factors amb signe.
        score = 0.0
        for f in factors:
            sign = -1.0 if f.direction == "subtract" else 1.0
            score += sign * f.contribution
        score = max(0.0, min(1.0, score))

        return PersonQuality(
            person_id=person.id,
            xref=person.xref,
            score=round(score, 2),
            missing=missing,
            factors=factors,
            issues=issues,
        )

    def evaluate(self, persons: list[Person], **kwargs) -> QualityReport:
        """Evalua un conjunt (kwargs s'apliquen a totes les persones)."""
        evaluations = [self.evaluate_person(p, **kwargs) for p in persons]
        avg = (
            sum(q.score for q in evaluations) / len(evaluations) if evaluations else 0.0
        )
        return QualityReport(
            average_score=round(avg, 2),
            evaluations=evaluations,
        )

    # ------------------------------------------------------------- factors
    def _add_basic_factors(
        self, person: Person, factors: list[QualityFactor], missing: list[str]
    ) -> None:
        name_contrib = 0.0
        if person.given_name:
            name_contrib += 0.15
        if person.surname:
            name_contrib += 0.1
        if person.given_name and person.surname:
            factors.append(
                QualityFactor("name", name_contrib, 0.25, "nom complet present")
            )
        else:
            missing.extend(
                attr
                for attr in ("given_name", "surname")
                if not getattr(person, attr, None)
            )
            factors.append(
                QualityFactor("name", name_contrib, 0.25, "nom incomplet", "subtract")
            )

        if person.sex:
            factors.append(QualityFactor("sex", 0.05, 0.05, "sexe registrat"))
        else:
            missing.append("sex")

    def _add_relationships_factors(
        self,
        factors: list[QualityFactor],
        has_parents: bool,
        has_children: bool,
        missing: list[str],
    ) -> None:
        if has_parents:
            factors.append(QualityFactor("parents", 0.15, 0.15, "pares identificats"))
        else:
            missing.append("parents")
        if has_children:
            factors.append(QualityFactor("children", 0.15, 0.15, "fills identificats"))
        else:
            missing.append("children")

    def _add_sources_factors(
        self,
        factors: list[QualityFactor],
        has_sources: bool,
        event_count: int,
        place_count: int,
        missing: list[str],
    ) -> None:
        if has_sources:
            factors.append(QualityFactor("sources", 0.15, 0.15, "fonts citades"))
        else:
            missing.append("sources")
        if event_count > 0:
            factors.append(
                QualityFactor("events", 0.1, 0.1, f"{event_count} esdeveniments")
            )
        else:
            missing.append("events")
        if place_count > 0:
            factors.append(QualityFactor("places", 0.05, 0.05, f"{place_count} llocs"))
        else:
            missing.append("places")

    def _add_chronology(
        self,
        person: Person,
        factors: list[QualityFactor],
        issues: list[str],
        has_chronology_issue: bool,
    ) -> None:
        if person.birth_date:
            factors.append(QualityFactor("birth", 0.1, 0.1, "naixement datat"))
        else:
            factors.append(QualityFactor("birth", 0.0, 0.1, "sense naixement datat"))
        if person.death_date:
            factors.append(QualityFactor("death", 0.05, 0.05, "defunció datada"))
        else:
            factors.append(QualityFactor("death", 0.0, 0.05, "sense defunció datada"))

        if has_chronology_issue:
            factors.append(
                QualityFactor("chronology", 0.2, 0.2, "error cronològic", "subtract")
            )
            issues.append("error cronològic (mort abans de naixement)")
        else:
            self._check_birth_before_death(person, factors, issues)

    def _check_birth_before_death(
        self,
        person: Person,
        factors: list[QualityFactor],
        issues: list[str],
    ) -> None:
        if not person.birth_date or not person.death_date:
            return
        engine = DateEngine()
        b, d = engine.parse(person.birth_date), engine.parse(person.death_date)
        if b.year is not None and d.year is not None and d.year < b.year:
            factors.append(
                QualityFactor(
                    "chronology", 0.2, 0.2, "defunció abans de naixement", "subtract"
                )
            )
            issues.append(f"mort ({d.year}) abans de naixement ({b.year})")
