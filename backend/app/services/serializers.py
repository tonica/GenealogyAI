"""Serialitzadors: converteixen objectes ORM en dictaris tipats.

Mante la lògica de presentació fora dels endpoints per separat-la i
poder-la provar independentment.
"""

from __future__ import annotations

from app.models import Event, Family, Person, Place


def place_out(place: Place) -> dict | None:
    if place is None:
        return None
    return {
        "id": place.id,
        "name": place.name,
        "latitude": place.latitude,
        "longitude": place.longitude,
    }


def event_out(event: Event) -> dict:
    return {
        "id": event.id,
        "event_type": event.event_type,
        "date_text": event.date_text,
        "date_iso": event.date_iso,
        "date_year": event.date_year,
        "place": place_out(event.place),
    }


def person_out(person: Person) -> dict:
    return {
        "id": person.id,
        "xref": person.xref,
        "given_name": person.given_name,
        "surname": person.surname,
        "prefix": person.prefix,
        "suffix": person.suffix,
        "sex": person.sex,
        "birth_date": person.birth_date,
        "death_date": person.death_date,
    }


def person_detail(person: Person) -> dict:
    data = person_out(person)
    data["notes"] = person.notes

    child_fams: list[Family] = [pc.family for pc in person.child_links if pc.family]
    spouse_fams: list[Family] = list(person.families_as_father) + list(
        person.families_as_mother
    )

    data["events"] = [event_out(e) for e in person.events]
    data["families_as_child"] = [
        {
            "id": f.id,
            "xref": f.xref,
            "father_id": f.father_id,
            "mother_id": f.mother_id,
            "father": person_out(f.father) if f.father else None,
            "mother": person_out(f.mother) if f.mother else None,
        }
        for f in child_fams
    ]
    data["families_as_spouse"] = [
        {
            "id": f.id,
            "xref": f.xref,
            "spouse_id": f.mother_id if f.father_id == person.id else f.father_id,
            "spouse": _other_parent(f, person),
            "marriage_date": f.marriage_date,
            "marriage_place": f.marriage_place,
        }
        for f in spouse_fams
    ]
    return data


def _other_parent(family: Family, person: Person) -> dict | None:
    other = family.father if family.mother_id == person.id else family.mother
    return person_out(other) if other else None


def family_out(family: Family) -> dict:
    children = sorted(
        (pc.child for pc in family.parent_children if pc.child),
        key=lambda c: _sibling_order(family, c),
    )
    return {
        "id": family.id,
        "xref": family.xref,
        "father": person_out(family.father) if family.father else None,
        "mother": person_out(family.mother) if family.mother else None,
        "children": [person_out(c) for c in children],
        "marriage_date": family.marriage_date,
        "marriage_place": family.marriage_place,
        "events": [event_out(e) for e in family.events],
    }


def _sibling_order(family: Family, child: Person) -> int:
    for pc in family.parent_children:
        if pc.child_id == child.id:
            return pc.sibling_order or 0
    return 0
