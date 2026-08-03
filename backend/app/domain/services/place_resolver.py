"""Servei de domínio `PlaceResolver`.

Unifica topònims: normalitza accents i espais, agrupa variants i genera
suggeriments de fusió. No escriu a BD: només suggeriments.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.value_objects import PlaceName


@dataclass
class PlaceSuggestion:
    """Suggeriment d'unificació entre un lloc i una possible variant."""

    canonical: str
    variants: list[str] = field(default_factory=list)
    reason: str = ""


class PlaceResolver:
    """Detecta variacions d'un mateix topònim i proposa unificació."""

    def __init__(self) -> None:
        self._accent_map = {
            "a": ["à", "á", "ä"],
            "e": ["è", "é", "ë"],
            "i": ["ì", "í", "ï"],
            "o": ["ò", "ó", "ö"],
            "u": ["ù", "ú", "ü"],
            "c": ["ç"],
        }

    def normalize(self, text: str) -> str:
        """Normalitza un topònim (minúscules, sense accents, espais únics)."""
        return PlaceName(name=text).normalized()

    def suggestions(self, places: list[str]) -> list[PlaceSuggestion]:
        """Agrupa llocs que son iguals un cop normalitzats.

        Retorna un suggeriment per grup: `canonical` és la variant més
        freqüent i `variants` les alternatives trobades.
        """
        groups: dict[str, set[str]] = {}
        for raw in places:
            norm = self.normalize(raw)
            if not norm:
                continue
            groups.setdefault(norm, set()).add(raw)

        result: list[PlaceSuggestion] = []
        for _norm, variants in groups.items():
            if len(variants) > 1:
                ordered = sorted(variants, key=lambda v: -len(v))
                canonical = ordered[0]
                result.append(
                    PlaceSuggestion(
                        canonical=canonical,
                        variants=list(ordered),
                        reason=f"totes normalitzen a '{_norm}'",
                    )
                )
        result.sort(key=lambda s: -len(s.variants))
        return result

    def detect_variant(self, a: str, b: str) -> bool:
        """Dues cadenes són variants del mateix lloc (normalitzades iguals)."""
        return bool(self.normalize(a)) and self.normalize(a) == self.normalize(b)

    def similarity(self, a: str, b: str) -> float:
        return PlaceName(name=a).similarity(PlaceName(name=b))
