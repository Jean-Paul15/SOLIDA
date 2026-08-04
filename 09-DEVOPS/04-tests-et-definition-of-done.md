# Tests et Definition of Done

## Pyramide

| Niveau | Part | Vitesse | Ce qui est testé |
|---|---|---|---|
| Domaine | 60 % | < 1 s au total | Règles métier pures |
| Application | 25 % | < 5 s | Cas d'usage avec doublures |
| Intégration | 12 % | < 2 min | Adaptateurs, base réelle |
| Bout en bout | 3 % | lent | Le parcours principal, uniquement |

Un seul test de bout en bout est indispensable : recherche → dossier → demande → score → fiche.
C'est le parcours de la démonstration. S'il casse, la démonstration casse.

## Ce qui doit être testé en priorité

Par ordre décroissant de coût d'une régression :

1. **Invariant de la scorecard** : somme des points = score
2. **Absence de fuite** : exclusion du sociétaire du taux de groupe, features à `date_reference`
3. **Cascade** : bascule socle / enrichi selon les quatre conditions
4. **Grille** : correspondance score → tranche, y compris aux bornes exactes
5. **Plafond progressif** : primo-emprunteur, coefficient, plafond produit
6. **Frontière** : écriture dans CORE-SIM refusée
7. **Contrôle d'accès** : cloisonnement par agence
8. **Formatage des montants** : jamais de flottant, séparateur correct

Les points 1, 2 et 6 sont ceux qui, s'ils cassent silencieusement, produisent un système qui
paraît fonctionner tout en étant faux. Ce sont les plus dangereux.

## Doublures

| Doublure | Usage |
|---|---|
| `LecteurCoreSimEnMemoire` | Tests d'application |
| `FeatureStoreEnMemoire` | Tests d'application |
| `ModeleConstant` | Renvoie une probabilité fixe. Permet de tester la scorecard sans modèle entraîné |

`ModeleConstant` est la doublure la plus utile : elle permet de développer et de tester toute la
chaîne score → points → grille → fiche **avant que le premier modèle n'existe**. C'est ce qui rend
possible le travail en parallèle du jour 1.

## Données de test

Un jeu de cas figés, versionné, couvrant : primo-emprunteur sans groupe, sociétaire de cycle 4 avec
groupe sain, sociétaire avec groupe dégradé, sociétaire avec incidents, sociétaire aux données
incomplètes, dossier aux bornes exactes de tranche.

Ces cas servent aussi de **jeu de démonstration**. Les préparer une fois sert deux fois.

## Definition of Done

Une tâche est terminée quand **tous** ces points sont vrais. Pas huit sur dix.

### Pour toute tâche
- [ ] Le code fait ce que la spécification décrit
- [ ] Lint et typage passent
- [ ] Les tests passent
- [ ] Aucun secret, aucune valeur en dur
- [ ] Aucun contrat d'interface modifié sans annonce
- [ ] La branche est à jour sur `main`
- [ ] Le commit suit la convention

### En plus, pour une règle métier
- [ ] Testée à 100 %, y compris les cas limites
- [ ] Aucune dépendance externe dans le test
- [ ] Le temps est injecté, pas appelé

### En plus, pour un endpoint
- [ ] Rôle vérifié
- [ ] Entrée validée
- [ ] Erreurs traduites en français
- [ ] Cloisonnement par agence appliqué

### En plus, pour un écran
- [ ] Les cinq états sont implémentés
- [ ] Navigable au clavier
- [ ] Aucune valeur de style hors jetons
- [ ] Aucun composant interdit
- [ ] Contraste vérifié
- [ ] Testé à 1366×768, résolution la plus probable en agence

### En plus, pour un modèle
- [ ] Journalisé dans MLflow
- [ ] Calibration vérifiée
- [ ] Métriques par segment
- [ ] Aucune variable sensible
- [ ] Invariant vérifié sur 1 000 dossiers

## Ce qui n'est pas une tâche terminée

« Ça marche chez moi », « je finirai les tests après », « c'est juste temporaire », « je committe
et je nettoie ensuite ». Ces phrases, sur trois jours, produisent le jour 3 une base de code que
personne ne peut faire démarrer.
