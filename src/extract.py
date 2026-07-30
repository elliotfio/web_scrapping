"""Extraction : lecture du HTML brut, aucun appel reseau ici.

Les selecteurs ont ete verifies manuellement sur des pages reelles de
https://kws.go.ke/parks/ le 2026-07-30 (voir docs/architecture.md,
rubrique "Ancrage des selecteurs").
"""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

# --- Page liste (/parks/) ------------------------------------------------
#
# Ancrage retenu : le lien <a> a l'interieur du titre <h4> de chaque carte
# parc (h4.fusion-title-heading a[href*="/park/"]).
# Pourquoi plus stable que l'alternative ecartee (l'ancre de fond de carte
# "a.fusion-column-anchor", purement decorative, sans texte) : le lien du
# titre porte a la fois l'URL ET le nom lisible du parc dans un element
# semantique de titre. Si le theme change son systeme de grille (classes
# "fusion-*" generees par le page builder), le lien du titre a de bonnes
# chances de survivre car il porte l'information affichee a l'utilisateur.
LIST_ITEM_SELECTOR = "h4.fusion-title-heading a[href*='/park/']"


def parse_list_page(html: str, base_url: str) -> list[dict]:
    """Retourne une liste de {"name": str, "url": str}, dedupliquee par URL."""
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict] = []
    seen_urls: set[str] = set()

    for link in soup.select(LIST_ITEM_SELECTOR):
        href = link.get("href")
        name = link.get_text(strip=True)
        if not href or not name:
            continue
        url = urljoin(base_url, href)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        items.append({"name": name, "url": url})

    return items


# --- Page detail (/park/<slug>/) -----------------------------------------
#
# Ancrage retenu pour le contenu editorial : le conteneur <div class="post-content">.
# Pourquoi plus stable que l'alternative ecartee (parcourir tous les <p> de
# la page) : la page KWS repete le meme paragraphe d'accroche institutionnelle
# ("We are committed to...") dans l'en-tete de chaque page. Chercher le premier
# <p> long sur toute la page capture ce texte generique au lieu du resume du
# parc. Restreindre la recherche a .post-content isole le corps editorial
# propre a chaque parc.
CONTENT_CONTAINER_SELECTOR = "div.post-content"

REGION_PATTERN = re.compile(r"located in ([A-Z][A-Za-z\-\s]+?County)", re.IGNORECASE)
FEE_PATTERN = re.compile(r"\b(USD|KES|Ksh)\s?\d", re.IGNORECASE)

TYPE_PATTERNS: list[tuple[str, str]] = [
    ("marine_national_park_reserve", r"marine national park"),
    ("marine_national_reserve", r"marine national reserve"),
    ("national_park", r"national park"),
    ("national_reserve", r"national reserve"),
    ("wildlife_sanctuary", r"wildlife sanctuary"),
    ("animal_orphanage", r"animal orphanage"),
    ("safari_walk", r"safari walk"),
    ("sanctuary", r"sanctuary"),
]


def infer_type(name: str) -> str:
    """Normalise le nom en un type de zone protegee (vocabulaire controle).

    Regle metier, pas d'implementation cachee : on cherche le motif le plus
    specifique en premier (ex. "marine national park" avant "national park")
    pour ne pas mal classer les reserves marines.
    """
    lowered = name.lower()
    for label, pattern in TYPE_PATTERNS:
        if re.search(pattern, lowered):
            return label
    return "other"


def parse_detail_page(html: str) -> dict:
    """Retourne {"region": str|None, "summary": str|None, "fees_present": bool}."""
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select_one(CONTENT_CONTAINER_SELECTOR)

    if container is None:
        # Repli signale : pas de disparition silencieuse. On retombe sur la
        # page entiere mais on le rend visible dans les traces d'execution.
        container = soup
        fallback_used = True
    else:
        fallback_used = False

    summary: Optional[str] = None
    region: Optional[str] = None

    for paragraph in container.find_all("p"):
        text = paragraph.get_text(" ", strip=True)
        if not text:
            continue
        if summary is None and len(text) > 80:
            summary = text
        if region is None:
            match = REGION_PATTERN.search(text)
            if match:
                region = match.group(1).strip()
        if summary and region:
            break

    container_text = container.get_text(" ", strip=True)
    fees_present = bool(FEE_PATTERN.search(container_text))

    return {
        "region": region,
        "summary": summary,
        "fees_present": fees_present,
        "fallback_container_used": fallback_used,
    }
