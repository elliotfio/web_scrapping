"""Normalisation et validation : regles metier, independantes du HTML."""
from __future__ import annotations

import re
from urllib.parse import urlparse

from .models import REQUIRED_FIELDS

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(text: str | None) -> str | None:
    """Collapse les espaces multiples (rencontres ex. "Sibiloi National  Park").

    Distingue explicitement une valeur absente (None) d'une chaine vide :
    un texte qui ne contient que des espaces devient None, pas "".
    """
    if text is None:
        return None
    collapsed = _WHITESPACE_RE.sub(" ", text).strip()
    return collapsed or None


def slug_from_url(url: str) -> str:
    """Identifiant stable : le dernier segment non vide du chemin d'URL.

    Regle de construction : https://kws.go.ke/park/<slug>/ -> <slug>.
    Stable tant que KWS conserve ce motif d'URL (documente dans le rapport,
    rubrique 3 : "si le site reorganise ses URL, l'identifiant change").
    """
    path = urlparse(url).path
    segments = [segment for segment in path.split("/") if segment]
    if not segments:
        raise ValueError(f"Impossible de deriver un identifiant depuis {url!r}")
    return segments[-1]


class Deduplicator:
    """Deduplique par identifiant stable (id), pas par objet Python."""

    def __init__(self) -> None:
        self._seen_ids: set[str] = set()

    def is_duplicate(self, record_id: str) -> bool:
        if record_id in self._seen_ids:
            return True
        self._seen_ids.add(record_id)
        return False


def validate_record(record: dict) -> tuple[bool, list[str]]:
    """Un champ obligatoire absent doit etre signale, jamais silencieux."""
    missing = [field for field in REQUIRED_FIELDS if not record.get(field)]
    return (len(missing) == 0, missing)
