"""Servei de domínio `ResearchTaskGenerator`.

Genera automàticament tasques de recerca (ResearchTask) a partir de
l'anàlisi de les persones: baptisme, matrimoni, defunció, revisar
possibles duplicats o verificar topònims. No executa cap cerca.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Person, ResearchTask
from app.domain.services.date_engine import DateEngine


@dataclass
class ResearchTaskSuggestion:
    """Tasca de recerca proposada (abans de ser entitat ResearchTask)."""

    person_id: int | None
    xref: str | None
    objective: str
    kind: str
    hypothesis: str | None = None
    related_person_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "person_id": self.person_id,
            "xref": self.xref,
            "objective": self.objective,
            "kind": self.kind,
            "hypothesis": self.hypothesis,
            "related_person_ids": list(self.related_person_ids),
        }


class ResearchTaskGenerator:
    """Genera `ResearchTask` / suggeriments per a la recerca."""

    def __init__(self) -> None:
        self._date_engine = DateEngine()

    def generate(
        self,
        persons: list[Person],
        duplicate_pairs: list[tuple[Person, Person, float]] | None = None,
    ) -> list[ResearchTaskSuggestion]:
        tasks: list[ResearchTaskSuggestion] = []
        for p in persons:
            tasks.extend(self._tasks_for_person(p))
        for a, b, score in duplicate_pairs or []:
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=a.id,
                    xref=a.xref,
                    objective=f"Revisar possible duplicat entre {a.display_name} i {b.display_name}",
                    kind="duplicate",
                    hypothesis=f"Similitud {score:.2f}",
                    related_person_ids=[b.id] if b.id is not None else [],
                )
            )
        return tasks

    def to_research_tasks(
        self, suggestions: list[ResearchTaskSuggestion]
    ) -> list[ResearchTask]:
        return [
            ResearchTask(
                person_id=s.person_id,
                objective=s.objective,
                hypothesis=s.hypothesis,
                related_person_ids=list(s.related_person_ids),
            )
            for s in suggestions
        ]

    def _tasks_for_person(self, p: Person) -> list[ResearchTaskSuggestion]:
        tasks: list[ResearchTaskSuggestion] = []

        if not p.birth_date:
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=p.id,
                    xref=p.xref,
                    objective="Buscar baptisme/naixement",
                    kind="birth",
                    hypothesis="Es desconeix la data de naixement",
                )
            )
        elif self._date_engine.parse(p.birth_date).precision.name == "YEAR":
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=p.id,
                    xref=p.xref,
                    objective="Precisar data de naixement (dia i mes)",
                    kind="birth",
                    hypothesis="Només es coneix l'any",
                )
            )

        if p.sex and not p.family_as_spouse_ids:
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=p.id,
                    xref=p.xref,
                    objective="Buscar matrimoni",
                    kind="marriage",
                    hypothesis="No consta cap unió",
                )
            )

        if not p.death_date:
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=p.id,
                    xref=p.xref,
                    objective="Buscar defunció",
                    kind="death",
                    hypothesis="Es desconeix la defunció",
                )
            )

        if not p.family_as_child_ids:
            tasks.append(
                ResearchTaskSuggestion(
                    person_id=p.id,
                    xref=p.xref,
                    objective="Identificar pares",
                    kind="parents",
                    hypothesis="No es coneix la família d'origen",
                )
            )
        return tasks
