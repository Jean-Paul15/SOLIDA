# Reprendre SOLIDA sur un autre PC

Utiliser d'abord le paquet privé `PAQUET_TRANSFERT_SOLIDA_*.zip`. Il contient les Parquet, le bundle EBM et les documents de contexte : aucune connexion réseau n'est nécessaire.

1. Cloner le dépôt puis extraire le ZIP à sa racine.
2. Vérifier ces trois fichiers :

```text
simulateur/sorties/credits.parquet
modelisation/data/processed/jeu_socle.parquet
modelisation/data/modeles/bundle_socle/manifeste.json
```

3. Suivre le fichier `LISEZ_MOI_AVANT_EXTRACTION.txt` livré dans le ZIP.
4. Pour reprendre le travail, lire dans cet ordre :
   - [Transmission complète](2026-09-13-transmission-complete.md) ;
   - [Décisions SOCLE EBM](../../modelisation/docs/decisions-socle.md) ;
   - [Questionnaire modèle enrichi](../../modelisation/docs/questionnaire-modele-enrichi.md) ;
   - [Constat Claude sur les plafonds](2026-09-13-constat-claude-plafonds.md) ;
   - [Journal de discussion](2026-09-13-journal-discussion.md) ;
   - [Contexte de reprise JSON](2026-09-13-contexte-reprise.json).

## Donner le contexte à un nouvel agent

Joindre le fichier `docs/continuite/2026-09-13-contexte-reprise.json` à la nouvelle discussion, puis envoyer cette instruction :

```text
Lis intégralement AGENTS.md, docs/continuite/2026-09-13-contexte-reprise.json,
docs/continuite/2026-09-13-transmission-complete.md et
modelisation/docs/questionnaire-modele-enrichi.md avant toute modification.
Les Parquet locaux sont dans simulateur/sorties/ et le bundle SOCLE dans
modelisation/data/modeles/bundle_socle/. Respecte les décisions déjà confirmées ;
pose les questions métier encore ouvertes avant d'implémenter le modèle enrichi,
la couche solidaire ou les seuils du moteur de décision.
```

`ACCES_DONNEES_LOCAL.txt` est confidentiel. Ne jamais l'ajouter à Git. Il n'est utile que pour récupérer plus tard les données avec DVC via le réseau ; il n'est pas nécessaire pour commencer avec le ZIP.
