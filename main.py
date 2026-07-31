"""Point d'entree du collecteur KWS (cible S09).

Usage :
    python main.py                       # utilise config.ini
    python main.py --max-items 5         # collecte limitee pour un test rapide
    python main.py --config config.ini --output output
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.config import load_config
from src.pipeline import run


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collecteur KWS - cible S09 (ProtectedArea)")
    parser.add_argument("--config", default="config.ini", help="chemin du fichier de configuration")
    parser.add_argument("--max-items", type=int, default=None, help="surcharge le plafond d'objets")
    parser.add_argument("--output", default=None, help="surcharge le dossier de sortie")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.max_items is not None:
        config.max_items = args.max_items
    if args.output is not None:
        config.output_dir = Path(args.output)

    stats = run(config)
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
