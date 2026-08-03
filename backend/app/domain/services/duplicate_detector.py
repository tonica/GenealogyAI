"""Servei de domínio `DuplicateDetector` basat en regles.

Arquitectura:
    DuplicateDetector
        -> Rules (NameRule, BirthRule, DeathRule, ParentsRule, ...)
        -> Score (agregació ponderada)
        -> Decision (DuplicateCandidate)

No fusiona mai: només genera candidats. Treballa exclusivament amb
entitats de domínio, sense SQL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.domain.entities import Person
from app.domain.services.duplicate_rules import DuplicateRule, RuleResult

if TYPE_CHECKING:
    pass


@dataclass
class DuplicateGroup:
    """Grup de persones candidates a ser la mateixa (retrocompatible)."""

    persons: list[Person] = field(default_factory=list)
    reason: str = ""

    @property
    def size(self) -> int:
        return len(self.persons)

    @property
    def ids(self) -> list[int]:
        return [p.id for p in self.persons if p.id is not None]


@dataclass
class DuplicateCandidate:
    """Parell de persones que poden ser la mateixa (decisió per regles)."""

    person_a: Person
    person_b: Person
    score: float
    confidence: float
    rules_used: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    @property
    def ids(self) -> tuple[int | None, int | None]:
        return self.person_a.id, self.person_b.id

    def to_dict(self) -> dict:
        return {
            "person_a": {
                "id": self.person_a.id,
                "xref": self.person_a.xref,
                "name": self.person_a.display_name,
            },
            "person_b": {
                "id": self.person_b.id,
                "xref": self.person_b.xref,
                "name": self.person_b.display_name,
            },
            "score": self.score,
            "confidence": self.confidence,
            "rules_used": list(self.rules_used),
            "reasons": list(self.reasons),
        }


class DuplicateDetector:
    """Motor de duplicats basat en regles configurable."""

    # Pesos per regla en la puntuació final.
    DEFAULT_WEIGHTS: dict[str, float] = {
        "name": 0.35,
        "birth": 0.2,
        "death": 0.1,
        "parents": 0.1,
        "marriage": 0.1,
        "children": 0.1,
        "place": 0.05,
    }

    def __init__(
        self,
        match_on_surname: bool = True,
        require_year: bool = False,
        threshold: float = 0.55,
        weights: dict[str, float] | None = None,
    ) -> None:
        self.match_on_surname = match_on_surname
        self.require_year = require_year
        self.threshold = threshold
        self.weights = dict(self.DEFAULT_WEIGHTS)
        if weights:
            self.weights.update(weights)

    # ------------------------------------------------------------- regles
    def _build_rules(self) -> list[DuplicateRule]:
        from app.domain.services.duplicate_rules import (
            BirthRule,
            ChildrenRule,
            DeathRule,
            MarriageRule,
            NameRule,
            ParentsRule,
            PlaceRule,
        )

        return [
            NameRule(),
            BirthRule(),
            DeathRule(),
            ParentsRule(),
            MarriageRule(),
            ChildrenRule(),
            PlaceRule(),
        ]

    def _aggregate(
        self, a: Person, b: Person
    ) -> tuple[float, float, list[str], list[str]]:
        """Executa totes les regles i agrega score/confiança."""
        total_weight = sum(w for name, w in self.weights.items())
        score = 0.0
        confidence = 0.0
        rules_used: list[str] = []
        reasons: list[str] = []
        for rule in self._build_rules():
            result: RuleResult = rule.evaluate(a, b)
            w = self.weights.get(rule.name, 0.0)
            if result.score > 0:
                score += w * result.score
                confidence += w * result.confidence
                rules_used.append(rule.name)
                reasons.append(result.reason)
        if total_weight:
            score /= total_weight
            confidence /= total_weight
        return (
            round(score, 3),
            round(confidence, 3),
            rules_used,
            reasons,
        )

    # --------------------------------------------------------- API pública
    def detect_candidates(self, persons: list[Person]) -> list[DuplicateCandidate]:
        """Compara parells i retorna candidats per sobre del llindar."""
        candidates: list[DuplicateCandidate] = []
        for i, a in enumerate(persons):
            for b in persons[i + 1 :]:
                if a.id is not None and a.id == b.id:
                    continue
                score, confidence, rules, reasons = self._aggregate(a, b)
                if score >= self.threshold:
                    candidates.append(
                        DuplicateCandidate(
                            person_a=a,
                            person_b=b,
                            score=score,
                            confidence=confidence,
                            rules_used=rules,
                            reasons=reasons,
                        )
                    )
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def find_duplicates(self, persons: list[Person]) -> list[DuplicateGroup]:
        """Agrupa persones que comparteixen nom + (cognom) + any de naixement.

        Manté la signatura original per compatibilitat amb l'API i tests
        previs, ara derivada de les regles.
        """
        from app.domain.value_objects import PersonName

        buckets: dict[tuple, list[Person]] = {}
        for p in persons:
            an = PersonName(given=p.given_name, surnames=p.surname)
            given = an.normalized() if an.given else ""
            surname = _norm(p.surname)
            if self.match_on_surname:
                key_parts = (given, surname)
            else:
                key_parts = (given,)
            if self.require_year and p.birth_date:
                year = self._year_of(p.birth_date)
                if year:
                    key_parts = key_parts + (year,)
            bucket_key = "*".join(part for part in key_parts if part)
            if bucket_key:
                buckets.setdefault(bucket_key, []).append(p)

        return [
            DuplicateGroup(persons=group, reason=f"nom similar ({key})")
            for key, group in buckets.items()
            if len(group) > 1
        ]

    def is_likely_duplicate(self, a: Person, b: Person) -> tuple[bool, str]:
        """Decisió booleana ràpida amb la regla de nom (retrocompatible)."""
        from app.domain.value_objects import PersonName

        an = PersonName(given=a.given_name, surnames=a.surname)
        bn = PersonName(given=b.given_name, surnames=b.surname)
        given = an.normalized() == bn.normalized() and bool(an.given)
        surname = _norm(a.surname) == _norm(b.surname) and bool(a.surname)
        if given and (surname or not self.match_on_surname):
            return True, "nom i cognom idèntics"
        if not given and surname:
            return False, "cognom idèntic però sense nom"
        return False, "no coincideix"

    @staticmethod
    def _year_of(date_text: str) -> str:
        import re

        m = re.search(r"\b(1[5-9]\d{2}|2\d{3})\b", date_text)
        return m.group(1) if m else ""


def _norm(value: str | None) -> str:
    if not value:
        return ""
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()
