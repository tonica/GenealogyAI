"""Tests de DataQualityReport, ResearchTaskGenerator i estadístiques ampliades."""

from __future__ import annotations

from app.domain.entities import Person
from app.domain.services import (
    DataQualityReport,
    DataQualityReportGenerator,
    QualityEngine,
    ResearchTaskGenerator,
    StatisticsEngine,
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


class TestQualityFinding:
    def test_to_dict(self):
        from app.domain.services.quality_report import QualityFinding

        f = QualityFinding("date", "warning", "missatge", ref="I1", metadata={"y": 1})
        d = f.to_dict()
        assert d["category"] == "date"
        assert d["severity"] == "warning"
        assert d["ref"] == "I1"
        assert d["metadata"] == {"y": 1}


class TestDataQualityReport:
    def test_severity_properties(self):
        from app.domain.services.quality_report import QualityFinding

        rep = DataQualityReport(
            findings=[
                QualityFinding("a", "error", "e"),
                QualityFinding("b", "warning", "w"),
                QualityFinding("c", "info", "i"),
            ]
        )
        assert len(rep.errors) == 1
        assert len(rep.warnings) == 1
        assert len(rep.infos) == 1
        assert rep.to_dict()["total"] == 3

    def test_to_json(self):
        import json

        d = DataQualityReport().to_json()
        assert json.loads(d)["total"] == 0

    def test_to_json_pretty(self):
        import json

        s = DataQualityReport().to_json(pretty=True)
        assert json.loads(s)["total"] == 0

    def test_to_markdown_empty(self):
        md = DataQualityReport().to_markdown()
        assert "Cap observació" in md

    def test_to_markdown_with_findings(self):
        from app.domain.services.quality_report import QualityFinding

        rep = DataQualityReport(findings=[QualityFinding("date", "warning", "data")])
        md = rep.to_markdown()
        assert "| warning |" in md


class TestDataQualityReportGenerator:
    def test_impossible_date(self):
        rep = DataQualityReportGenerator().generate([_p(1, "Joan", "Miró", "999")])
        cats = [f.category for f in rep.warnings]
        assert "date" in cats

    def test_missing_birth(self):
        rep = DataQualityReportGenerator().generate([_p(1, "Joan", "Miró")])
        msgs = [f.message for f in rep.warnings]
        assert any("naixement" in m for m in msgs)

    def test_chronology_error(self):
        rep = DataQualityReportGenerator().generate(
            [_p(1, "Joan", "Miró", "1900", "1850")]
        )
        cats = [f.category for f in rep.errors]
        assert "chronology" in cats

    def test_duplicate_found(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, "Joan", "Miró", "1893")]
        rep = DataQualityReportGenerator().generate(people)
        cats = [f.category for f in rep.warnings]
        assert "duplicate" in cats

    def test_places_variants(self):
        rep = DataQualityReportGenerator().generate(
            [_p(1, "Joan", "Miró")], places=["Cataluña", "Cataluna"]
        )
        cats = [f.category for f in rep.warnings]
        assert "place" in cats

    def test_name_variants_info(self):
        rep = DataQualityReportGenerator().generate(
            [_p(1, "Maria", "Miró"), _p(2, "María", "Puig")]
        )
        cats = [f.category for f in rep.infos]
        assert "name" in cats

    def test_missing_family_links(self):
        rep = DataQualityReportGenerator().generate([_p(1, "Joan", "Miró")])
        cats = [f.category for f in rep.warnings]
        assert "relationships" in cats


class TestResearchTaskGenerator:
    def test_missing_life_events(self):
        p = _p(1, "Joan", "Miró", sex="M")
        tasks = ResearchTaskGenerator().generate([p])
        kinds = {t.kind for t in tasks}
        assert {"birth", "death", "parents", "marriage"} <= kinds

    def test_precise_birth(self):
        p = _p(1, "Joan", "Miró", "1893")
        tasks = ResearchTaskGenerator().generate([p])
        kinds = {t.kind for t in tasks}
        assert "birth" in kinds  # només l'any -> precisar data

    def test_duplicate_tasks(self):
        a = _p(1, "Joan", "Miró")
        b = _p(2, "Joan", "Miró")
        tasks = ResearchTaskGenerator().generate([a, b], [(a, b, 0.8)])
        kinds = [t.kind for t in tasks]
        assert "duplicate" in kinds
        dup = next(t for t in tasks if t.kind == "duplicate")
        assert dup.related_person_ids == [2]

    def test_to_research_tasks(self):
        from app.domain.entities import ResearchTask

        tasks = ResearchTaskGenerator().to_research_tasks(
            ResearchTaskGenerator().generate([_p(1, "Joan", "Miró")])
        )
        assert tasks
        assert isinstance(tasks[0], ResearchTask)

    def test_to_dict(self):
        t = ResearchTaskGenerator().generate([_p(1, "Joan", "Miró")])[0]
        d = t.to_dict()
        assert d["person_id"] == 1
        assert "objective" in d


class TestStatisticsExtended:
    def test_males_females(self):
        people = [
            _p(1, "Joan", "Miró", sex="M"),
            _p(2, "Anna", "Puig", sex="F"),
            _p(3, None, None, sex="U"),
        ]
        stats = StatisticsEngine().compute(people, [], [])
        assert stats.males == 1
        assert stats.females == 1

    def test_average_age(self):
        people = [_p(1, "Joan", "Miró", "1900", "1960")]
        stats = StatisticsEngine().compute(people, [], [])
        assert stats.average_age == 60.0
        assert stats.max_age == 60

    def test_births_deaths_by_year(self):
        people = [
            _p(1, "Joan", "Miró", "1900", "1960"),
            _p(2, "Anna", "Puig", "1900"),
        ]
        stats = StatisticsEngine().compute(people, [], [])
        assert stats.births_by_year[1900] == 2
        assert stats.deaths_by_year[1960] == 1

    def test_persons_without_data(self):
        people = [_p(1, None, None), _p(2, "Joan", "Miró", "1900")]
        stats = StatisticsEngine().compute(people, [], [])
        assert stats.persons_without_data == 1

    def test_largest_branches(self):
        from app.domain.entities import Family

        fam = Family(id=1, child_ids=[1, 2, 3])
        stats = StatisticsEngine().compute([], [fam], [])
        assert stats.largest_branches == [3]

    def test_top_places(self):
        from app.domain.entities import Event, Place

        place = Place(id=1, name="Barcelona")
        events = [
            Event(id=1, event_type="birth", person_id=1, place_id=1, place=place),
            Event(id=2, event_type="birth", person_id=2, place_id=1, place=place),
        ]
        stats = StatisticsEngine().compute([], [], events)
        assert stats.top_places == [("Barcelona", 2)]

    def test_events_by_type(self):
        from app.domain.entities import Event

        events = [Event(id=1, event_type="birth", person_id=1)]
        stats = StatisticsEngine().compute([], [], events)
        assert stats.events_by_type["birth"] == 1

    def test_to_dict(self):
        stats = StatisticsEngine().compute([_p(1, "Joan", "Miró", "1900")], [], [])
        d = stats.to_dict()
        assert d["persons"] == 1
        assert d["sex_by"] == {"M": 1}
        assert d["top_surnames"] == [{"surname": "Miró", "count": 1}]


class TestQualityEngineExtended:
    def test_complete_person_high_score(self):
        p = _p(1, "Joan", "Miró", "1893")
        q = QualityEngine().evaluate_person(
            p, has_parents=True, has_children=True, event_count=3, place_count=1
        )
        assert q.score >= 0.6
        assert "parents" not in q.missing

    def test_chronology_issue_reduces_score(self):
        a = QualityEngine().evaluate_person(_p(1, "Joan", "Miró", "1900"))
        b = QualityEngine().evaluate_person(
            _p(2, "Joan", "Miró", "1900"), has_chronology_issue=True
        )
        assert b.score < a.score
        assert b.issues

    def test_factor_lookup(self):
        q = QualityEngine().evaluate_person(_p(1, "Joan", "Miró", "1893"))
        assert q.factor("name") is not None
        assert q.factor("nope") is None

    def test_to_dict(self):
        q = QualityEngine().evaluate_person(_p(1, "Joan", "Miró", "1893"))
        d = q.to_dict()
        assert d["person_id"] == 1
        assert "factors" in d
        assert d["factors"][0]["name"] == "name"

    def test_birth_before_death_check(self):
        p = _p(1, "Joan", "Miró", "1950", "1900")
        q = QualityEngine().evaluate_person(p)
        assert "cronol" in " ".join(q.issues).lower() or any(
            "abans" in i for i in q.issues
        )

    def test_report_distribution(self):
        people = [_p(1, "Joan", "Miró", "1893"), _p(2, None, None)]
        report = QualityEngine().evaluate(people)
        dist = report.distribution
        assert sum(dist.values()) == 2
        d = report.to_dict()
        assert d["average_score"] == report.average_score
