# Protocole obligatoire pour les agents (Claude Code, Codex)

Ce fichier est la première chose à lire avant toute action sur le dépôt SOLIDA.
Il s'applique intégralement à Claude Code et à Codex. Il n'est pas indicatif.

---

## 1. Règle zéro : ne jamais inventer une décision

Si l'information nécessaire n'est pas dans `03-MODELE/`, `07-MLOPS/` ou `docs/` (backend,
frontend, infra), elle n'a pas été tranchée.

**Interdit :** deviner un nom de champ, inventer un seuil, choisir une librairie non listée,
créer un endpoint non spécifié, ajouter une dépendance, modifier un contrat d'interface.

**Attendu :** s'arrêter, énoncer précisément l'information manquante, proposer deux ou trois options
avec leurs conséquences, et attendre l'arbitrage humain.

Formulation attendue :

```
DÉCISION MANQUANTE
Contexte : je dois implémenter X (fichier Y).
Ce qui manque : le seuil de Z n'est défini nulle part dans la documentation de référence
(03-MODELE/, docs/).
Options :
  A) ... conséquence ...
  B) ... conséquence ...
Recommandation : A, parce que ...
J'attends l'arbitrage avant de continuer.
```

---

## 2. Protocole de recherche obligatoire avant décision technique

Avant toute décision structurante (choix de librairie, d'algorithme, de pattern, de version,
de configuration de production), l'agent **doit** :

1. **Chercher** la documentation officielle en ligne, pas se fier à sa mémoire d'entraînement.
2. **Confronter au moins deux sources**, dont une officielle (documentation de l'éditeur, RFC,
   spécification), et non deux billets de blog.
3. **Vérifier la version** : les APIs de Next.js, Tailwind, shadcn/ui, FastAPI, scikit-learn et
   MLflow changent vite. Une réponse correcte pour une version antérieure est une réponse fausse.
4. **Écrire ce qu'il a trouvé** avant de coder : source, date, version concernée, conclusion.
5. **Signaler les contradictions** entre sources plutôt que de choisir silencieusement.

Cette étape n'est pas facultative parce qu'elle est lente. Une décision structurante mal prise coûte
plus cher que trente minutes de vérification.

**Cas où la recherche est obligatoire :**

- Toute version de librairie à épingler
- Toute API dont la signature n'est pas certaine à 100 %
- Toute configuration de sécurité (hachage, JWT, CORS, en-têtes)
- Tout paramètre de production (pooling, timeouts, limites)
- Toute norme métier (BCEAO, taux d'usure, seuils prudentiels)

---

## 3. Périmètre et frontières

L'agent ne modifie que les fichiers relevant du module qui lui a été confié.
S'il pense qu'un fichier hors de son périmètre doit changer, il le signale sans le modifier.

**Ne jamais toucher sans instruction explicite :**

- Les ports et contrats du domaine (`backend/solida/domain/ports/`, `backend/solida/domain/values/`)
  et leur implémentation
- Le schéma de la base CORE-SIM
- Les fichiers de configuration d'environnement
- Les migrations déjà appliquées
- Les dossiers de référence eux-mêmes (`03-MODELE/`, `07-MLOPS/`)

---

## 4. Ordre de travail imposé

Pour toute tâche, dans cet ordre, sans sauter d'étape :

1. Lire le ou les fichiers de `03-MODELE/`, `07-MLOPS/` ou `docs/` couvrant le périmètre.
2. Reformuler la tâche en une phrase et énoncer le critère de réussite.
3. Lister les fichiers qui seront créés ou modifiés, **avant** de les écrire.
4. Vérifier que rien dans la liste ne viole un contrat existant.
5. Écrire les tests d'abord quand la logique est déterministe (règles métier, scorecard, cascade).
6. Implémenter.
7. Exécuter lint, types et tests. Ne jamais annoncer une tâche terminée sans les avoir exécutés.
8. Résumer en trois lignes : ce qui a été fait, ce qui reste, ce qui a été supposé.

---

## 5. Interdits absolus

| Interdit | Raison |
|---|---|
| Écrire dans la base CORE-SIM depuis SOLIDA | Violation de la frontière structurante du projet |
| Mettre un secret en dur dans le code | Sécurité, et détecté par les hooks |
| Ajouter une dépendance non listée dans `backend/pyproject.toml` ou `frontend/package.json` | Dérive de stack |
| Utiliser `localStorage`/`sessionStorage` pour des données métier | Non conforme à la politique de persistance |
| Générer des données de démonstration dans le code applicatif | Les données viennent du simulateur, pas du code |
| Introduire une variable sensible dans le modèle (sexe, ethnie, religion) | Engagement de non-discrimination du projet |
| Livrer un modèle sans vérification de calibration | La scorecard perd tout sens |
| Contourner un test qui échoue en le désactivant | Dette masquée |
| Reformater un fichier entier en même temps qu'un changement fonctionnel | Diff illisible |

---

## 6. Style de production attendu

- **Lisible avant malin.** Le code sera relu sous pression, à 23h, par quelqu'un d'autre.
- **Petites unités.** Une fonction fait une chose. Un fichier a un sujet.
- **Nommage métier en français** pour le domaine (`societaire`, `groupe_caution`, `score_octroi`),
  **anglais pour la technique** (`repository`, `handler`, `client`). Ne pas mélanger dans un même nom.
- **Pas de commentaire qui paraphrase le code.** Un commentaire explique un *pourquoi* non évident.
- **Typage strict** partout (Python : annotations complètes ; TypeScript : pas de `any`).
- **Erreurs explicites.** Jamais d'exception avalée silencieusement.

---

## 7. Communication

- Répondre en français.
- Pas de flatterie, pas de préambule. Aller au fait.
- Signaler les incertitudes plutôt que de les lisser.
- Quand une instruction du dossier paraît fausse ou contradictoire, **le dire** au lieu de l'appliquer
  mécaniquement. Ce dossier est faillible.

---

## 8. Rappel du contexte produit

SOLIDA est un système de scoring d'octroi de microcrédit destiné à des coopératives financières
d'Afrique de l'Ouest disposant de ressources informatiques limitées. Trois conséquences permanentes
sur toutes les décisions techniques :

1. **Légèreté** : pas de GPU, pas de dépendance à un service cloud propriétaire, fonctionnement
   sur un serveur modeste.
2. **Explicabilité** : toute décision produite doit être justifiable variable par variable auprès
   d'un sociétaire.
3. **Souveraineté** : les données ne quittent pas le périmètre de la coopérative.

Une solution techniquement brillante qui viole l'un de ces trois points est une mauvaise solution.
