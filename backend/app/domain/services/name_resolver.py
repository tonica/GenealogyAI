"""Servei de domínio `NameResolver`.

Detecta variants de noms (Carbonel/Carbonell/Carbonnell, Jose/José/Josep,
Maria/María) i genera suggeriments sense modificar res.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.value_objects import PersonName


@dataclass
class NameSuggestion:
    """Suggeriment de normalització/variant per a un nom."""

    original: str
    normalized: str
    alternatives: list[str] = field(default_factory=list)
    reason: str = ""


# Parells comuns en català/castellà per al context català.
_COMMON_VARIANTS: dict[str, set[str]] = {
    "jose": {"jose", "josé", "josep"},
    "maria": {"maria", "maría"},
    "joan": {"joan", "juan"},
    "pau": {"pau", "pablo"},
    "pere": {"pere", "pedro", "pedre"},
}


class NameResolver:
    """Resol variants de noms per generar suggeriments."""

    def normalize(self, text: str) -> str:
        """Normalitza un nom (minúscules, sense accents)."""
        return PersonName(given=text).normalized() if text else ""

    def suggestions(self, names: list[str]) -> list[NameSuggestion]:
        """Agrupa variants del mateix nom i suggereix la forma canònica."""
        groups: dict[str, set[str]] = {}
        for name in names:
            norm = self.normalize(name)
            if not norm:
                continue
            groups.setdefault(norm, set()).add(name)

        result: list[NameSuggestion] = []
        for _norm, variants in groups.items():
            if len(variants) > 1:
                ordered = sorted(variants, key=lambda v: -len(v))
                canonical = ordered[0]
                result.append(
                    NameSuggestion(
                        original=canonical,
                        normalized=_norm,
                        alternatives=list(ordered[1:]),
                        reason=f"variants normalitzades a '{_norm}'",
                    )
                )
        result.sort(key=lambda s: -len(s.alternatives))
        return result

    def detect_variant(self, a: str, b: str) -> bool:
        """Dos noms són variants del mateix (normalitzats iguals)."""
        na, nb = self.normalize(a), self.normalize(b)
        return bool(na) and na == nb

    def known_variants(self, text: str) -> list[str]:
        """Retorna variants conegudes (dels parells comuns) d'un nom."""
        norm = self.normalize(text)
        for canonical, variants in _COMMON_VARIANTS.items():
            if norm in variants:
                return sorted(variants - {norm})
        return []
