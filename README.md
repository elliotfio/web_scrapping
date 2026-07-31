# Collecteur KWS — cible S09 (Kenya Wildlife Service)

TP individuel — Web Scraping moderne et industrialisation.

## Cible et perimetre

- Site : Kenya Wildlife Service — https://kws.go.ke/parks/
- Objet collecte : `ProtectedArea` (parc national, reserve, sanctuaire, etc.)
- Volume : 60 objets maximum (fiche de cible), 35 parcs disponibles au
  30/07/2026 -> l'integralite du catalogue est collectee sans depasser le
  plafond.
- Aucune donnee animale sensible n'est collectee (contrainte de la fiche de
  cible), uniquement des metadonnees publiques sur les zones protegees
  elles-memes.

## Prerequis

- Python 3.9 ou plus recent.
- Acces reseau sortant vers `kws.go.ke` pour une collecte reelle (les tests
  n'en ont pas besoin, voir plus bas).

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example config.ini
```

`config.ini` ne contient aucun secret : la cible est publique. Ajustez
`delay_seconds` et `max_items` si besoin.

## Lancer une collecte limitee

```bash
python main.py --max-items 5
```

Produit `output/protected_areas.json` et `output/protected_areas.csv`, et
affiche des traces horodatees (vus, acceptes, rejetes, doublons, exportes,
requetes envoyees).

Pour une collecte complete (dans la limite du plafond de la fiche de cible) :

```bash
python main.py
```

## Verification (sans reseau)

```bash
pytest tests/ -v
```

Les tests rejouent l'extraction sur des pages HTML enregistrees dans
`tests/fixtures/` (capturees le 2026-07-30) et couvrent les trois controles
demandes : nombre d'objets extraits d'une page enregistree, une
normalisation (regions et espaces), et la deduplication / le rejet d'un
objet incomplet.

## Architecture

Voir [docs/architecture.md](docs/architecture.md) pour le schema du flux de
donnees, le tableau composant/responsabilite, et la justification des deux
decisions structurantes.

## Format de sortie

`ProtectedArea` : `id, name, type, region, summary, url, fees_present,
source_url, collected_at`. Voir [samples/sample_output.json](samples/sample_output.json)
pour un echantillon reel.

- `id` : slug de l'URL canonique (ex. `tsavo-east-national-park`), stable
  tant que KWS conserve son motif d'URL `/park/<slug>/`.
- `type` : vocabulaire controle derive du nom (`national_park`,
  `national_reserve`, `marine_national_park_reserve`, `wildlife_sanctuary`,
  `animal_orphanage`, `safari_walk`, `sanctuary`, `other`).
- `fees_present` : booleen, presence d'un montant (USD/KES/Ksh) dans le
  corps editorial de la fiche parc — heuristique, voir limites ci-dessous.
- Valeur absente vs vide : un champ non trouve devient `null` en JSON, pas
  une chaine vide.

## Limites connues

- `fees_present` est une heuristique par motif monetaire dans le texte : un
  parc qui annoncerait une gratuite ou un tarif dans un format inhabituel
  pourrait etre mal classe.
- `region` depend d'un motif textuel (« located in X County ») present dans
  la plupart des fiches mais pas garanti sur toutes (ex. reserves marines
  au phrase differente) ; le champ vaut alors `null`, sans qu'une erreur ne
  soit levee.
- Aucune pagination sur `/parks/` au 30/07/2026 (divergence avec la fiche de
  cible, qui l'annoncait) : documentee, pas corrigee de force.

## Usage responsable

- `robots.txt` verifie avant toute collecte : seul `/wp-admin/` est
  interdit, aucun `Crawl-delay` declare.
- Debit faible : une requete a la fois, delai configurable
  (`delay_seconds`, 1,5 s par defaut) entre deux requetes.
- Aucune authentification, aucune action irreversible, aucune donnee
  personnelle collectee.

## Usage de l'IA

Voir [docs/AI_USAGE.md](docs/AI_USAGE.md).
