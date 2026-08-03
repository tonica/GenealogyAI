"""Tests de domain services (sense SQLite ni infraestructura).

S'usen entitats `Person` del domínio directament construïdes.
"""

from __future__ import annotations

from app.domain.entities import Person
from app.domain.services import DuplicateDetector, QualityEngine, StatisticsEngine


def _p(person_id, given, surname, birth=None, sex="M"):
    return Person(
        id=person_id, given_name=given, surname=surname, birth_date=birth, sex=sex
    )


class TestDuplicateDetector:
    def test_finds_exact_duplicate(self):
        people = [_p(1, "Joan", "Miró"), _p(2, "Joan", "Miró")]
        groups = DuplicateDetector().find_duplicates(people)
        assert len(groups) == 1
        assert groups[0].size == 2
        assert groups[0].ids == [1, 2]

    def test_distinguishes_similar_names(self):
        people = [_p(1, "Joan", "Miró"), _p(2, "Josep", "Miró")]
        groups = DuplicateDetector().find_duplicates(people)
        assert groups == []

    def test_require_year_filters(self):
        people = [
            _p(1, "Joan", "Miró", "1893"),
            _p(2, "Joan", "Miró", "1893"),
            _p(3, "Joan", "Miró", None),
        ]
        groups = DuplicateDetector(require_year=True).find_duplicates(people)
        assert len(groups) == 1
        assert groups[0].ids == [1, 2]

    def test_surdiacritic_insensitive(self):
        people = [_p(1, "Joan", "Miró"), _p(2, "Joan", "Miro")]
        groups = DuplicateDetector().find_duplicates(people)
        assert len(groups) == 1


class TestStatisticsEngine:
    def test_computes_counts(self):
        people = [_p(1, "Joan", "Miró", sex="M"), _p(2, "Anna", "Puig", sex="F")]
        stats = StatisticsEngine().compute(
            persons=people,
            families=[],
            events=[],
        )
        assert stats.persons == 2
        assert stats.sex_by["M"] == 1
        assert stats.sex_by["F"] == 1
        assert stats.surname_frequency["Miró"] == 1

    def test_without_name_comptador(self):
        people = [_p(1, None, None), _p(2, "Joan", "Miró")]
        stats = StatisticsEngine().compute(people, [], [])
        assert stats.persons_without_name == 1


class TestQualityEngine:
    def test_complete_person_scores_high(self):
        p = _p(1, "Joan", "Miró", "1893")
        q = QualityEngine().evaluate_person(p)
        assert q.score > 0
        assert "surname" not in q.missing

    def test_incomplete_person_lists_missing(self):
        p = Person(id=1, sex=None)
        q = QualityEngine().evaluate_person(p)
        assert "given_name" in q.missing
        assert q.score == 0.0

    def test_report_average(self):
        people = [_p(1, "Joan", "Miró"), _p(2, None, None)]
        report = QualityEngine().evaluate(people)
        assert report.average_score > 0
        assert len(report.evaluations) == 2
