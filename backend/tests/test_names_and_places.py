"""Tests de PersonName/PlaceName ampliats i dels resolvers de noms i llocs."""

from __future__ import annotations

from app.domain.services import NameResolver, PlaceResolver
from app.domain.value_objects import PersonName, PlaceName


class TestPersonNameExtended:
    def test_normalized(self):
        n = PersonName(given="José", surnames="Carbonell")
        assert n.normalized() == "jose carbonell"

    def test_search_name(self):
        n = PersonName(given="Joan", surnames="Miró")
        assert n.search_name == "Joan Miró"

    def test_initials(self):
        n = PersonName(given="Joan", middle="Pau", surnames="Miró")
        assert n.initials() == "J. P. M."

    def test_initials_skip_non_alpha(self):
        n = PersonName(given="")
        assert n.initials() == ""

    def test_phonetic_key_same_for_similar(self):
        a = PersonName(given="Carbonell")
        b = PersonName(given="Carbonel")
        assert a.phonetic_key() == b.phonetic_key()

    def test_similarity_identical(self):
        a = PersonName(given="Joan", surnames="Miró")
        b = PersonName(given="Joan", surnames="Miró")
        assert a.similarity(b) == 1.0

    def test_similarity_empty(self):
        assert PersonName().similarity(PersonName(given="Joan")) == 0.0

    def test_similarity_phonetic_match(self):
        a = PersonName(given="Jose")
        b = PersonName(given="José")
        assert a.similarity(b) >= 0.55

    def test_display_name(self):
        n = PersonName(given="Joan", middle="", surnames="Miró")
        assert n.display_name() == "Joan Miró"

    def test_from_given_surname_none(self):
        n = PersonName.from_given_surname(None, None)
        assert n.given is None
        assert n.surnames is None
        assert n.full_name == ""


class TestPlaceNameExtended:
    def test_tokens_skip_stopwords(self):
        p = PlaceName(name="Sant Julià de Lòria")
        toks = p.tokens
        assert "julia" in toks
        assert "de" not in toks

    def test_similarity_same(self):
        a = PlaceName(name="Barcelona")
        b = PlaceName(name="Barcelona")
        assert a.similarity(b) == 1.0

    def test_similarity_partial(self):
        a = PlaceName(name="Argentona")
        b = PlaceName(name="Argentona Barcelona")
        assert 0 < a.similarity(b) < 1.0

    def test_contains(self):
        a = PlaceName(name="Barcelona Sarrià")
        b = PlaceName(name="Barcelona")
        assert a.contains(b)

    def test_matches_exact(self):
        a = PlaceName(name="Barcelona")
        b = PlaceName(name="Barcelona")
        assert a.matches(b)

    def test_matches_high_similarity(self):
        a = PlaceName(name="San Julián de Argentina")
        b = PlaceName(name="San Julian de Argentina")
        assert a.matches(b)

    def test_canonical_name_method(self):
        p = PlaceName(name="Barcelona")
        assert p.canonical_name() == "barcelona"

    def test_display_name_method(self):
        p = PlaceName(name="Barcelona")
        assert p.display_name() == "Barcelona"


class TestNameResolver:
    def test_normalize(self):
        assert NameResolver().normalize("José") == "jose"

    def test_normalize_empty(self):
        assert NameResolver().normalize("") == ""

    def test_suggestions_groups_variants(self):
        r = NameResolver()
        sugs = r.suggestions(["Maria", "María", "Joan"])
        assert len(sugs) == 1
        assert sugs[0].original in {"Maria", "María"}
        assert len(sugs[0].alternatives) == 1

    def test_suggestions_no_variants(self):
        assert NameResolver().suggestions(["Joan", "Pere"]) == []

    def test_detect_variant(self):
        assert NameResolver().detect_variant("Maria", "María") is True
        assert NameResolver().detect_variant("Maria", "Pere") is False

    def test_known_variants(self):
        r = NameResolver()
        v = r.known_variants("José")
        assert "josep" in v
        assert NameResolver().known_variants("Alfons") == []


class TestPlaceResolver:
    def test_normalize(self):
        assert PlaceResolver().normalize("Barcelona, Cataluña") == "barcelona, cataluna"

    def test_suggestions(self):
        r = PlaceResolver()
        sugs = r.suggestions(["Cataluña", "Cataluna", "Barcelona"])
        assert len(sugs) == 1
        assert sugs[0].canonical in {"Cataluna", "Cataluña"}
        assert len(sugs[0].variants) == 2

    def test_detect_variant(self):
        r = PlaceResolver()
        assert r.detect_variant("Cataluña", "Cataluna") is True
        assert r.detect_variant("Barcelona", "Girona") is False

    def test_similarity(self):
        r = PlaceResolver()
        assert r.similarity("Barcelona", "Barcelona") == 1.0
