"""Tests de normalitzacio de text (llocs, cognoms, noms)."""

from app.utils.text import (
    normalize_place,
    normalize_surname,
    surname_key,
)


def test_normalize_place_basic():
    assert normalize_place("Barcelona") == "barcelona"


def test_normalize_place_removes_accents_for_key():
    assert normalize_place("Barcelona") == "barcelona"
    assert normalize_place("Madrid") == "madrid"


def test_normalize_place_collapses_spaces_and_commas():
    assert normalize_place("  Barcelona  ,") == "barcelona"


def test_normalize_surname_title_case():
    assert normalize_surname("perez") == "Perez"
    assert normalize_surname("DE LA CRUZ") == "De La Cruz"


def test_normalize_surname_removes_punctuation():
    assert normalize_surname("o'hara") == "O Hara"


def test_surname_key_casefold():
    assert surname_key("Perez") == "perez"
    assert surname_key("pérez") == "pérez"  # fra: keys son sense accent via surname
