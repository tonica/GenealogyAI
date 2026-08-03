"""Servei de domínio `DataQualityReport`.

Genera un informe complet de qualitat de dades: dates impossibles,
duplicats, persones sense naixement/defunció/família, llocs repetits,
topònims inconsistents i errors cronològics. Exportable a JSON i Markdown.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from app.domain.entities import Person
from app.domain.services.date_engine import DateEngine
from app.domain.services.duplicate_detector import DuplicateDetector
from app.domain.services.name_resolver import NameResolver
from app.domain.services.place_resolver import PlaceResolver


@dataclass
class QualityFinding:
    """Una observació de qualitat amb severitat."""

    category: str
    severity: str  # "error" | "warning" | "info"
    message: str
    ref: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "message": self.message,
            "ref": self.ref,
            "metadata": self.metadata,
        }


@dataclass
class DataQualityReport:
    """Informe complet de qualitat de dades."""

    findings: list[QualityFinding] = field(default_factory=list)

    @property
    def errors(self) -> list[QualityFinding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[QualityFinding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def infos(self) -> list[QualityFinding]:
        return [f for f in self.findings if f.severity == "info"]

    def to_dict(self) -> dict:
        return {
            "total": len(self.findings),
            "errors": [f.to_dict() for f in self.errors],
            "warnings": [f.to_dict() for f in self.warnings],
            "infos": [f.to_dict() for f in self.infos],
        }

    def to_json(self, pretty: bool = False) -> str:
        return json.dumps(
            self.to_dict(), ensure_ascii=False, indent=2 if pretty else None
        )

    def to_markdown(self) -> str:
        lines = ["# Informe de qualitat de dades", ""]
        lines.append(f"**Total observacions:** {len(self.findings)}")
        lines.append(
            f"**Errors:** {len(self.errors)} · **Warnings:** {len(self.warnings)}"
        )
        lines.append("")
        if not self.findings:
            lines.append("_Cap observació detectada._")
            return "\n".join(lines)
        lines.append("## Observacions")
        lines.append("")
        lines.append("| Severitat | Categoria | Ref | Missatge |")
        lines.append("|---|---|---|---|")
        for f in self.findings:
            lines.append(
                f"| {f.severity} | {f.category} | {f.ref or '-'} | {f.message} |"
            )
        lines.append("")
        return "\n".join(lines)


class DataQualityReportGenerator:
    """Genera el `DataQualityReport` a partir de persones i llocs."""

    def __init__(
        self,
        duplicate_threshold: float = 0.55,
    ) -> None:
        self._date_engine = DateEngine()
        self._duplicate_detector = DuplicateDetector(threshold=duplicate_threshold)
        self._place_resolver = PlaceResolver()
        self._name_resolver = NameResolver()

    def generate(
        self,
        persons: list[Person],
        places: list[str] | None = None,
    ) -> DataQualityReport:
        findings: list[QualityFinding] = []
        self._check_impossible_dates(persons, findings)
        self._check_missing_life_events(persons, findings)
        self._check_chronology(persons, findings)
        self._check_duplicates(persons, findings)
        self._check_family_links(persons, findings)
        if places:
            self._check_places(places, findings)
        self._check_name_variants(persons, findings)
        return DataQualityReport(findings=findings)

    # ------------------------------------------------------------------
    def _check_impossible_dates(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        for p in persons:
            for attr, label in (
                ("birth_date", "naixement"),
                ("death_date", "defunció"),
            ):
                raw = getattr(p, attr, None)
                if not raw:
                    continue
                dv = self._date_engine.parse(raw)
                if not dv.valid or dv.year is None or not (1500 <= dv.year <= 2100):
                    findings.append(
                        QualityFinding(
                            "date",
                            "warning",
                            f"data de {label} impossible: '{raw}'",
                            ref=p.xref,
                            metadata={"year": dv.year},
                        )
                    )

    def _check_missing_life_events(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        for p in persons:
            if not p.birth_date:
                findings.append(
                    QualityFinding(
                        "completeness", "warning", "persona sense naixement", ref=p.xref
                    )
                )
            if not p.death_date and p.sex and not _is_historic(p):
                findings.append(
                    QualityFinding(
                        "completeness", "info", "persona sense defunció", ref=p.xref
                    )
                )

    def _check_chronology(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        for p in persons:
            if not p.birth_date or not p.death_date:
                continue
            b = self._date_engine.parse(p.birth_date)
            d = self._date_engine.parse(p.death_date)
            if b.year is not None and d.year is not None and d.year < b.year:
                findings.append(
                    QualityFinding(
                        "chronology",
                        "error",
                        f"defunció ({d.year}) abans de naixement ({b.year})",
                        ref=p.xref,
                    )
                )

    def _check_duplicates(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        for cand in self._duplicate_detector.detect_candidates(persons):
            findings.append(
                QualityFinding(
                    "duplicate",
                    "warning",
                    f"possible duplicat ({cand.reasons[0] if cand.reasons else 'noms similars'})",
                    ref=f"{cand.person_a.xref or cand.person_a.id} / {cand.person_b.xref or cand.person_b.id}",
                    metadata={"score": cand.score},
                )
            )

    def _check_family_links(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        for p in persons:
            if not p.family_as_child_ids:
                findings.append(
                    QualityFinding(
                        "relationships", "warning", "persona sense pares", ref=p.xref
                    )
                )
            if not p.family_as_spouse_ids:
                findings.append(
                    QualityFinding(
                        "relationships",
                        "info",
                        "persona sense família pròpia",
                        ref=p.xref,
                    )
                )

    def _check_places(self, places: list[str], findings: list[QualityFinding]) -> None:
        for suggestion in self._place_resolver.suggestions(places):
            findings.append(
                QualityFinding(
                    "place",
                    "warning",
                    f"topònims inconsistents: {', '.join(suggestion.variants)}",
                    ref=suggestion.canonical,
                    metadata={"variants": suggestion.variants},
                )
            )

    def _check_name_variants(
        self, persons: list[Person], findings: list[QualityFinding]
    ) -> None:
        given_names = [p.given_name for p in persons if p.given_name]
        for suggestion in self._name_resolver.suggestions(given_names):
            findings.append(
                QualityFinding(
                    "name",
                    "info",
                    f"variants de nom: {', '.join(suggestion.alternatives)}",
                    ref=suggestion.original,
                    metadata={"alternatives": suggestion.alternatives},
                )
            )


def _is_historic(p: Person) -> bool:
    """Heurística: persones nascudes abans de 1850 no tenen defunció coneguda."""
    if not p.birth_date:
        return False
    import re

    m = re.search(r"\b(1[5-8]\d{2})\b", p.birth_date)
    return m is not None
