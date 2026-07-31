# Architecture

## Flux de donnees (6 responsabilites)

```
config.ini                (configuration)
     |
     v
ThrottledClient.get()      (acquisition : debit controle, retries, compteur)
     |  HTML brut
     v
parse_list_page()          (extraction - liste)
parse_detail_page()        (extraction - detail)
     |  dict bruts
     v
normalize_whitespace()
slug_from_url() / infer_type()
validate_record()          (normalisation & validation)
     |  ProtectedArea valides
     v
export_json() / export_csv()   (export)
     |
     v
logging (module logging, horodate)   (journalisation & erreurs)
```

## Composants -> fichiers

| Responsabilite | Fichier | Entree | Sortie |
|---|---|---|---|
| Configuration | `src/config.py` | `config.ini` | `Config` |
| Acquisition | `src/http_client.py` | URL | `requests.Response`, compteur de requetes |
| Extraction | `src/extract.py` | HTML brut | listes/dicts (name, url, region, summary, fees_present) |
| Normalisation et validation | `src/normalize.py` | dicts bruts | valeurs normalisees, `(bool, missing_fields)` |
| Export | `src/export.py` | `list[ProtectedArea]` | `output/protected_areas.json`, `.csv` |
| Journalisation | `src/pipeline.py` (module `logging`) | evenements du run | logs horodates + compteurs vus/acceptes/rejetes/exportes |

`main.py` est le seul point d'entree CLI ; il ne contient aucune logique metier,
uniquement le cablage config -> pipeline.

## Decisions structurantes

**Decision 1 — client HTTP direct (`requests`) plutot qu'un navigateur piloté.**
Le diagnostic (rubrique 2.2 du rapport) montre que la reponse HTTP brute de
`https://kws.go.ke/parks/` contient deja les 35 liens de parcs et que chaque
page detail contient deja son paragraphe descriptif et son tableau de tarifs
dans le HTML initial (verifie en comparant la reponse `curl` brute au DOM
affiche). Un navigateur (Selenium/Playwright) aurait ete plus lourd, plus
lent et plus fragile pour un gain nul. Alternative ecartee : Playwright,
retenu pour les cibles qui necessitent une execution JavaScript (ce n'est pas
le cas ici).

**Decision 2 — extraction par selecteur CSS scope a `.post-content`, avec
repli signale plutot que valeur devinee.** L'alternative ecartee etait de
chercher le premier `<p>` de plus de 80 caracteres sur toute la page : elle
capturait a tort le paragraphe institutionnel repete en en-tete de chaque
page ("We are committed to..."). Restreindre au conteneur `.post-content`
isole le corps editorial propre a chaque parc. Si ce conteneur disparait
(changement de theme), le code ne plante pas silencieusement : il retombe
sur la page entiere et journalise un avertissement explicite
(`fallback_container_used`), pour que la regression soit visible dans les
traces plutot que dans des donnees fausses.

## Ancrage des selecteurs (detail, cf. rapport rubrique 5)

Voir les commentaires en tete de `src/extract.py` pour la justification
complete de `LIST_ITEM_SELECTOR` et `CONTENT_CONTAINER_SELECTOR`, avec les
alternatives ecartees et le comportement prevu en cas de rupture.
