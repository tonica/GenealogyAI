"""Construcció de l'arbre geneaològic (ascendents) des de la BDD."""

from __future__ import annotations

from app.models import Person


def _person_year(person: Person) -> int | None:
    for ev in person.events:
        if ev.event_type == "birth" and ev.date_year is not None:
            return ev.date_year
    return None


def _death_year(person: Person) -> int | None:
    for ev in person.events:
        if ev.event_type == "death" and ev.date_year is not None:
            return ev.date_year
    return None


def _tree_person(person: Person) -> dict:
    return {
        "id": person.id,
        "xref": person.xref,
        "given_name": person.given_name,
        "surname": person.surname,
        "birth_year": _person_year(person),
        "death_year": _death_year(person),
        "sex": person.sex,
        "parents": [],
    }


def _get_parents(person: Person) -> list[Person]:
    parents: list[Person] = []
    seen: set[int] = set()
    for pc in person.child_links:  # cada fill connectat a una família
        fam = pc.family
        if fam is None:
            continue
        for candidate in (fam.father, fam.mother):
            if candidate is not None and candidate.id not in seen:
                seen.add(candidate.id)
                parents.append(candidate)
    return parents


def build_tree(root: Person, max_depth: int = 3) -> dict:
    """Retorna l'arbre de progenitors (BFS) arrelat a `root`."""

    visited: set[int] = set()

    def build(node: dict, person: Person, depth: int) -> None:
        if depth >= max_depth:
            return
        if person.id in visited:
            return
        visited.add(person.id)
        for parent in _get_parents(person):
            child_node = _tree_person(parent)
            node["parents"].append(child_node)
            build(child_node, parent, depth + 1)

    root_node = _tree_person(root)
    build(root_node, root, 0)

    def _count(node: dict) -> int:
        return 1 + sum(_count(c) for c in node["parents"])

    count = _count(root_node)
    return {"root": root_node, "depth": max_depth, "person_count": count}
