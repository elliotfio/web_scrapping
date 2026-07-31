"""Orchestration : acquisition -> extraction -> normalisation/validation -> export.

Separe volontairement de main.py pour rester testable sans reseau (les
fonctions d'extraction/normalisation appelees ici sont les memes que celles
couvertes par tests/test_extraction.py).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from .config import Config
from .export import export_csv, export_json
from .extract import infer_type, parse_detail_page, parse_list_page
from .http_client import ThrottledClient
from .models import ProtectedArea
from .normalize import Deduplicator, normalize_whitespace, slug_from_url, validate_record

logger = logging.getLogger("kws_collector.pipeline")


def run(config: Config) -> dict:
    client = ThrottledClient(
        user_agent=config.user_agent,
        delay_seconds=config.delay_seconds,
        timeout_seconds=config.timeout_seconds,
        max_retries=config.max_retries,
    )
    dedup = Deduplicator()

    stats = {"seen": 0, "accepted": 0, "rejected": 0, "duplicates": 0, "exported": 0}
    records: list[ProtectedArea] = []

    logger.info("Debut de la collecte : %s (plafond=%s)", config.base_url, config.max_items)
    list_response = client.get(config.base_url)
    items = parse_list_page(list_response.text, config.base_url)
    logger.info("Page liste analysee : %s parcs trouves", len(items))

    for item in items[: config.max_items]:
        stats["seen"] += 1
        name = normalize_whitespace(item["name"])
        url = item["url"]

        try:
            record_id = slug_from_url(url)
        except ValueError as exc:
            logger.error("Objet rejete (identifiant impossible) : %s", exc)
            stats["rejected"] += 1
            continue

        if dedup.is_duplicate(record_id):
            logger.warning("Doublon ignore : %s (%s)", name, record_id)
            stats["duplicates"] += 1
            continue

        try:
            detail_response = client.get(url)
        except Exception as exc:  # noqa: BLE001 - erreur reseau signalee puis on continue
            logger.error("Page detail inaccessible pour %s (%s) : %s", name, url, exc)
            stats["rejected"] += 1
            continue

        detail = parse_detail_page(detail_response.text)
        if detail["fallback_container_used"]:
            logger.warning("Conteneur .post-content absent sur %s : extraction en repli sur la page entiere", url)

        candidate = {
            "id": record_id,
            "name": name,
            "type": infer_type(name),
            "region": normalize_whitespace(detail["region"]),
            "summary": normalize_whitespace(detail["summary"]),
            "url": url,
            "fees_present": detail["fees_present"],
            "source_url": url,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }

        is_valid, missing = validate_record(candidate)
        if not is_valid:
            logger.error("Objet rejete, champs obligatoires manquants %s : %s", missing, url)
            stats["rejected"] += 1
            continue

        records.append(ProtectedArea(**candidate))
        stats["accepted"] += 1

    output_json = config.output_dir / "protected_areas.json"
    output_csv = config.output_dir / "protected_areas.csv"
    export_json(records, output_json)
    export_csv(records, output_csv)
    stats["exported"] = len(records)
    stats["requests_sent"] = client.request_count

    logger.info(
        "Collecte terminee : vus=%s acceptes=%s rejetes=%s doublons=%s exportes=%s requetes=%s",
        stats["seen"], stats["accepted"], stats["rejected"], stats["duplicates"],
        stats["exported"], stats["requests_sent"],
    )
    return stats
