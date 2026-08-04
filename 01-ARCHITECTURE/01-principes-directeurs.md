# Principes directeurs

Neuf principes. En cas de conflit entre deux d'entre eux, le plus haut dans la liste l'emporte.

---

## 1. La frontière avant tout

CORE-SIM et SOLIDA sont deux systèmes. Toute confusion entre les deux est une faute d'architecture,
pas un raccourci acceptable. Voir `06-frontiere-sim-vs-solida.md`.

## 2. Séparer ce qui change de ce qui ne change pas

C'est le principe qui rend possible le travail en parallèle et le remplacement des données
synthétiques par des données réelles.

| Ne change pas | Change |
|---|---|
| Les contrats d'interface | Les implémentations derrière |
| Les règles métier | Leurs paramètres (seuils, PDO, taux) |
| La structure du générateur | Les proportions générées |
| Le pipeline de features | La liste des features |

Conséquence opérationnelle : **tout paramètre vit dans un fichier de configuration, jamais dans le
code**. Un seuil en dur est un défaut, pas un détail.

## 3. Le domaine ne dépend de rien

La logique métier (score, cascade, grille, crédit progressif) ne connaît ni PostgreSQL, ni FastAPI,
ni scikit-learn, ni MinIO. Elle se teste sans base de données, sans réseau et sans modèle entraîné.
Si un test de règle métier a besoin de Docker, l'architecture est cassée.

## 4. Dépendre d'abstractions, jamais d'implémentations

Chaque ressource externe est atteinte à travers un **port** défini dans le domaine et implémenté par
un **adaptateur** en périphérie. Le port `LecteurCoreSim` est défini par nos besoins, pas par le
schéma de la base. Le jour où le vrai SI d'une IMF remplace CORE-SIM, on écrit un nouvel adaptateur
et rien d'autre ne bouge. C'est l'argument de déployabilité que nous vendons au jury : il doit être
vrai dans le code.

## 5. Explicabilité par construction, pas par ajout

Le chemin qui va de la probabilité au score, du score aux points, des points à la fiche, est un
chemin **déterministe et testable**. Aucune approximation post-hoc. Si une évolution du modèle
casse la décomposition exacte en points, c'est l'évolution qu'on abandonne, pas l'explicabilité.

## 6. Dégradation gracieuse

Chaque composant définit son comportement en cas d'indisponibilité de ce dont il dépend.

| Indisponible | Comportement attendu |
|---|---|
| Agrégats solidaires (segment groupe) | Repli sur le socle individuel, mention explicite dans la réponse |
| Modèle enrichi | Repli sur le socle, mention explicite |
| MinIO | La fiche s'affiche à l'écran, l'archivage est différé |
| CORE-SIM | Erreur explicite, jamais de score sur données partielles silencieuses |

Un score calculé sur des données incomplètes sans le dire est pire qu'une absence de score.

## 7. Traçabilité de toute décision

Chaque score produit est persisté avec : version du modèle, version de la grille, valeurs d'entrée,
score, tranche, points par variable, identifiant de l'agent, horodatage. Sans cela, il n'y a ni
audit, ni recalibrage, ni défense de la décision face à un sociétaire.

## 8. Le coût d'exploitation est un critère de conception

Chaque composant ajouté doit répondre à : « une coopérative de 25 000 sociétaires avec un serveur
modeste et un informaticien à temps partiel peut-elle l'exploiter ? » Si la réponse est non, le
composant est écarté, aussi élégant soit-il.

## 9. Rendre le mauvais chemin difficile

Les règles ne suffisent pas, il faut des garde-fous mécaniques : utilisateur base en lecture seule
sur CORE-SIM, hooks Git qui bloquent les secrets, types stricts, tests de contrat sur les
interfaces, linter configuré pour interdire les imports croisant les couches.

---

## Anti-patterns explicitement proscrits

| Anti-pattern | Pourquoi c'est interdit ici |
|---|---|
| Logique métier dans un contrôleur HTTP | Rend la règle intestable et non réutilisable en batch |
| Modèle ML appelé directement depuis l'API | Empêche le versionnage et le repli |
| Requête SQL dans un composant React | Effondre la frontière client / serveur |
| Seuil, taux ou PDO en dur dans le code | Empêche le paramétrage par institution |
| Champ ajouté au feature store sans passer par le contrat | Rompt la reproductibilité |
| `try/except` sans traitement ni journalisation | Masque les pannes en production |
| Fonction qui lit la base *et* calcule *et* écrit | Viole la responsabilité unique, intestable |
