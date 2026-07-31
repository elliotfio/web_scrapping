"""Verification rejouable sans reseau (TP, rubrique 6).

Ces tests ne font aucun appel HTTP : ils rejouent l'extraction sur des
pages HTML enregistrees le 2026-07-30 dans tests/fixtures/. Les trois
controles demandes par l'enonce sont couverts explicitement :

    1. test_parse_list_page_returns_expected_count
    2. test_region_normalization_collapses_whitespace_and_extracts_county
    3. test_deduplication_and_incomplete_rejection
"""
from __future__ import annotations

from pathlib import Path

from src.extract import infer_type, parse_detail_page, parse_list_page
from src.normalize import Deduplicator, normalize_whitespace, slug_from_url, validate_record

FIXTURES = Path(__file__).parent / "fixtures"
BASE_URL = "https://kws.go.ke/parks/"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# --- Controle 1 : nombre d'objets extraits d'une page enregistree --------

def test_parse_list_page_returns_expected_count():
    html = load_fixture("parks_list.html")
    items = parse_list_page(html, BASE_URL)

    # Compte verifie manuellement sur la page enregistree (35 cartes parc,
    # liens dedupliques par URL). Un changement de ce nombre signale une
    # rupture de l'ancrage ou une evolution reelle du site.
    assert len(items) == 35
    assert all(item["url"].startswith("https://kws.go.ke/park/") for item in items)
    assert {"name": "Tsavo East National Park", "url": "https://kws.go.ke/park/tsavo-east-national-park/"} in items


# --- Controle 2 : une normalisation (region / espaces) --------------------

def test_region_normalization_collapses_whitespace_and_extracts_county():
    html = load_fixture("park_detail_tsavo_east.html")
    detail = parse_detail_page(html)

    assert detail["region"] == "Taita-Taveta County"

    # La normalisation d'espaces doit fusionner les doubles espaces observes
    # dans le HTML source (ex. "Sibiloi National  Park") sans rien inventer.
    assert normalize_whitespace("Sibiloi National  Park") == "Sibiloi National Park"
    assert normalize_whitespace("   ") is None  # valeur absente, pas une chaine vide
    assert normalize_whitespace(None) is None


def test_infer_type_prefers_the_most_specific_pattern():
    assert infer_type("Tsavo East National Park") == "national_park"
    assert infer_type("Kisite Mpunguti Marine National Park") == "marine_national_park_reserve"
    assert infer_type("Shimba Hills National Reserve") == "national_reserve"
    assert infer_type("Lake Elementaita Wildlife Sanctuary") == "wildlife_sanctuary"


# --- Controle 3 : deduplication et rejet d'un objet incomplet -------------

def test_deduplication_and_incomplete_rejection():
    dedup = Deduplicator()

    first_id = slug_from_url("https://kws.go.ke/park/tsavo-east-national-park/")
    duplicate_id = slug_from_url("https://kws.go.ke/park/tsavo-east-national-park/")
    other_id = slug_from_url("https://kws.go.ke/park/tsavo-west-national-park/")

    assert dedup.is_duplicate(first_id) is False
    assert dedup.is_duplicate(duplicate_id) is True  # meme slug -> doublon detecte
    assert dedup.is_duplicate(other_id) is False

    complete_record = {
        "id": "tsavo-east-national-park",
        "name": "Tsavo East National Park",
        "type": "national_park",
        "url": "https://kws.go.ke/park/tsavo-east-national-park/",
    }
    incomplete_record = {
        "id": "tsavo-east-national-park",
        "name": "",  # champ obligatoire vide
        "type": "national_park",
        "url": "https://kws.go.ke/park/tsavo-east-national-park/",
    }

    is_valid, missing = validate_record(complete_record)
    assert is_valid is True
    assert missing == []

    is_valid, missing = validate_record(incomplete_record)
    assert is_valid is False
    assert "name" in missing
