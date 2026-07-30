"""Chargement de la configuration depuis config.ini (voir config.example)."""
from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    base_url: str
    user_agent: str
    delay_seconds: float
    timeout_seconds: float
    max_retries: int
    max_items: int
    output_dir: Path


def load_config(path: str | Path = "config.ini") -> Config:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier de configuration introuvable : {path}. "
            "Copiez config.example vers config.ini avant de lancer le collecteur."
        )

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    section = parser["scraping"]

    return Config(
        base_url=section.get("base_url"),
        user_agent=section.get("user_agent"),
        delay_seconds=section.getfloat("delay_seconds", fallback=1.5),
        timeout_seconds=section.getfloat("timeout_seconds", fallback=15),
        max_retries=section.getint("max_retries", fallback=3),
        max_items=section.getint("max_items", fallback=60),
        output_dir=Path(section.get("output_dir", fallback="output")),
    )
