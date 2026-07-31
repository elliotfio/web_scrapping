# Usage de l'IA

> Ce fichier doit etre complete honnetement avant la remise. Le TP autorise
> l'usage de l'IA et ne le penalise pas, mais exige une declaration exacte,
> verifiee, et la capacite a expliquer/modifier tout le code rendu.

## Outils utilises

- Claude (Anthropic), via Claude Code, pour la generation du squelette
  initial du projet (structure de fichiers, client HTTP throttle,
  extraction, normalisation, export, tests, documentation).

## Taches confiees a l'IA

- Diagnostic initial de la cible (verification du `robots.txt`, comparaison
  reponse HTTP brute / structure attendue) sur `https://kws.go.ke/parks/`.
- Redaction des selecteurs d'extraction (`src/extract.py`) a partir de
  pages HTML reellement recuperees et inspectees.
- Mise en place de l'architecture en couches (config / acquisition /
  extraction / normalisation / export / journalisation) et des tests hors
  reseau.

## Exemples de demandes significatives

1. « Diagnostique la cible S09 (KWS) : robots.txt, presence du contenu sans
   JavaScript, structure de la page liste et d'une page detail. »
2. « Construis le collecteur (acquisition/extraction/normalisation/export)
   avec throttling configurable et verification rejouable sans reseau. »

<!-- A completer par l'eleve : ajoutez vos propres demandes si vous avez
     poursuivi le travail (nouveaux champs, correctifs, refactoring). -->

## Ce qui a ete verifie (a completer par l'eleve)

- [ ] J'ai relu chaque fichier de `src/` et je peux expliquer ligne par
      ligne ce qu'il fait.
- [ ] J'ai execute `pytest tests/ -v` moi-meme et je comprends pourquoi
      chaque test passe (et ce qui le ferait echouer).
- [ ] J'ai lance une collecte limitee (`python main.py --max-items 5`) et
      compare la sortie au site reel.
- [ ] J'ai verifie manuellement au moins un enregistrement produit (region,
      type, fees_present) en rouvrant la page source correspondante.

<!-- Remplacez les cases ci-dessus par des faits reels, pas par une
     coche automatique. Une case cochee sans verification reelle est
     precisement ce que la rubrique 10 de la notice sanctionne. -->

## Proposition de l'IA corrigee ou refusee, et pourquoi

<!-- A completer par l'eleve. Exemple de trame : la premiere version de
     l'extraction du champ "region" cherchait le motif sur toute la page et
     capturait un texte generique repete en en-tete ; elle a ete restreinte
     au conteneur .post-content apres verification sur une page reelle.
     Si vous avez trouve un autre probleme (ou aucun), decrivez-le ici avec
     vos propres mots et vos propres tests. -->

## Declaration

<!-- Si vous n'avez utilise aucune IA au-dela de ce point de depart, ce
     fichier reste tel quel : il documente deja l'usage initial. Si vous
     poursuivez seul(e) a partir d'ici, indiquez-le explicitement. -->
