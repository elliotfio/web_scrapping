"""Objet metier ProtectedArea (cible S09 - Kenya Wildlife Service)."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class ProtectedArea:
    # Identifiant stable : le slug KWS (dernier segment de l'URL canonique,
    # ex. "tsavo-east-national-park"). Voir docs/architecture.md pour la
    # justification de ce choix face a un identifiant genere localement.
    id: str
    name: str
    type: str
    region: Optional[str]
    summary: Optional[str]
    url: str
    fees_present: bool

    # Tracabilite, exigee par l'enonce du TP (rubrique 2 - modele de donnees).
    source_url: str
    collected_at: str

    def to_dict(self) -> dict:
        return asdict(self)


REQUIRED_FIELDS = ("id", "name", "type", "url")
