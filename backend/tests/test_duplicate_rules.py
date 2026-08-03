"""Tests de les regles de duplicació i del DuplicateDetector per regles."""

from __future__ import annotations

from app.domain.entities import Person
from app.domain.services import DuplicateDetector
from app.domain.services.duplicate_rules import (
    BirthRule,
    ChildrenRule,
    DeathRule,
    MarriageRule,
    NameRule,
    ParentsRule,
    PlaceRule,
    RuleResult,
)


def _p(person_id, given=None, surname=None, birth=None, death=None, sex="M"):
    return Person(
        id=person_id,
        given_name=given,
        surname=surname,
        birth_date=birth,
        death_date=death,
        sex=sex,
    )


class TestNameRule:
    def test_identical_names(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        r = NameRule().evaluate(a, b)
        assert r.score > 0.8
        assert "similar" in r.reason

    def test_none_both(self):
        r = NameRule().evaluate(_p(1), _p(2))
        assert r.score == 0.0

    def test_phonetic_similar(self):
        a = _p(1, "Josep", "Carbonell")
        b = _p(2, "Josef", "Carbonell")
        r = NameRule().evaluate(a, b)
        assert r.score > 0.5


class TestBirthRule:
    def test_same_year(self):
        r = BirthRule().evaluate(_p(1, birth="1893"), _p(2, birth="1893"))
        assert r.score == 1.0
        assert r.confidence == 0.9

    def test_missing_date(self):
        r = BirthRule().evaluate(_p(1, birth="1893"), _p(2))
        assert r.score == 0.0

    def test_close_years(self):
        r = BirthRule().evaluate(_p(1, birth="1893"), _p(2, birth="1894"))
        assert r.score == 0.5

    def test_different_years(self):
        r = BirthRule().evaluate(_p(1, birth="1893"), _p(2, birth="1920"))
        assert r.score == 0.0


class TestDeathRule:
    def test_same_year(self):
        r = DeathRule().evaluate(_p(1, death="1960"), _p(2, death="1960"))
        assert r.score == 1.0

    def test_missing(self):
        r = DeathRule().evaluate(_p(1, death="1960"), _p(2))
        assert r.score == 0.0


class TestParentsRule:
    def test_shared_family(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a.family_as_child_ids = [7]
        b.family_as_child_ids = [7]
        r = ParentsRule().evaluate(a, b)
        assert r.score == 1.0

    def test_no_family_data(self):
        r = ParentsRule().evaluate(_p(1, "Joan", "Miró"), _p(2, "Joan", "Miró"))
        assert r.score == 0.0

    def test_different_families(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a.family_as_child_ids = [1]
        b.family_as_child_ids = [2]
        r = ParentsRule().evaluate(a, b)
        assert r.score == 0.2


class TestMarriageRule:
    def test_shared_spouse_family(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a.family_as_spouse_ids = [3]
        b.family_as_spouse_ids = [3]
        r = MarriageRule().evaluate(a, b)
        assert r.score == 1.0

    def test_no_data(self):
        r = MarriageRule().evaluate(_p(1, "Joan", "Miró"), _p(2, "Joan", "Miró"))
        assert r.score == 0.0


class TestChildrenRule:
    def test_shared_children(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a._children_ids = [10, 11, 12]
        b._children_ids = [10, 11, 12]
        r = ChildrenRule().evaluate(a, b)
        assert r.score == 1.0

    def test_no_children(self):
        r = ChildrenRule().evaluate(_p(1, "Joan", "Miró"), _p(2, "Joan", "Miró"))
        assert r.score == 0.0

    def test_partial_overlap(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a._children_ids = [10, 11, 12]
        b._children_ids = [10, 99]
        r = ChildrenRule().evaluate(a, b)
        assert 0 < r.score < 1.0


class TestPlaceRule:
    def test_same_place(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a.birth_place = "Barcelona"
        b.birth_place = "Barcelona"
        r = PlaceRule().evaluate(a, b)
        assert r.score == 1.0

    def test_no_place(self):
        r = PlaceRule().evaluate(_p(1, "Joan", "Miró"), _p(2, "Joan", "Miró"))
        assert r.score == 0.0

    def test_related_place(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        a.birth_place = "Barcelona"
        b.birth_place = "Barcelona, Cataluña"
        r = PlaceRule().evaluate(a, b)
        assert r.score == 0.7


class TestDuplicateDetectorCandidates:
    def test_detects_candidate(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        cands = DuplicateDetector(threshold=0.5).detect_candidates(people)
        assert len(cands) == 1
        assert cands[0].score >= 0.5
        assert "name" in cands[0].rules_used
        assert cands[0].ids == (1, 2)

    def test_no_candidates_for_different(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Pere", "Vidal", "1920")]
        cands = DuplicateDetector().detect_candidates(people)
        assert cands == []

    def test_skips_same_id(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(1, "Joan", "Miró", "1893")]
        cands = DuplicateDetector(threshold=0.5).detect_candidates(people)
        assert cands == []

    def test_high_threshold_filters(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        cands = DuplicateDetector(threshold=0.99).detect_candidates(people)
        assert cands == []

    def test_to_dict(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        cand = DuplicateDetector(threshold=0.5).detect_candidates(people)[0]
        d = cand.to_dict()
        assert d["person_a"]["id"] == 1
        assert d["person_b"]["name"] == "Joan Miró"
        assert "score" in d

    def test_custom_weights(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        det = DuplicateDetector(threshold=0.5, weights={"name": 1.0})
        cands = det.detect_candidates(people)
        assert cands

    def test_find_duplicates_backward_compat(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        groups = DuplicateDetector().find_duplicates(people)
        assert len(groups) == 1

    def test_is_likely_duplicate(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        ok, reason = DuplicateDetector().is_likely_duplicate(a, b)
        assert ok is True
        assert reason

    def test_rule_result_repr(self):
        r = RuleResult(0.5, "motiu", 0.4)
        assert r.score == 0.5
        assert r.reason == "motiu"
