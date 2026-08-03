"""Servei de domínio `QualityEngine`.

Valora la qualitat de les dades per persona (completesa de camps vitals,
dates, llocs) i retorna un informe agregat. Pura lógica de domínio, sense
I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Person


@dataclass
class PersonQuality:
    """Qualitat d'una persona individual."""

    person_id: int | None = None
    xref: str | None = None
    score: float = 0.0
    missing: list[str] = field(default_factory=list)


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


class QualityEngine:
    """Puntua la completesa de cada persona."""

    # Pesos dels camps per a la puntuació (0..1).
    _WEIGHTS = {
        "given_name": 0.3,
        "surname": 0.25,
        "sex": 0.1,
        "birth_date": 0.15,
        "death_date": 0.1,
        "notes": 0.1,
    }

    def evaluate_person(self, person: Person) -> PersonQuality:
        score = 0.0
        missing: list[str] = []
        for attr, weight in self._WEIGHTS.items():
            value = getattr(person, attr, None)
            if value:
                score += weight
            else:
                missing.append(attr)
        return PersonQuality(
            person_id=person.id,
            xref=person.xref,
            score=round(score, 2),
            missing=missing,
        )

    def evaluate(self, persons: list[Person]) -> QualityReport:
        evaluations = [self.evaluate_person(p) for p in persons]
        avg = (
            sum(q.score for q in evaluations) / len(evaluations) if evaluations else 0.0
        )
        return QualityReport(
            average_score=round(avg, 2),
            evaluations=evaluations,
        )
