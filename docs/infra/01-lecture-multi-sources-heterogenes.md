# Interroger plusieurs bases hétérogènes en lecture seule (MySQL / Postgres / Oracle)

Contexte : plusieurs coopératives peuvent exposer leur système d'information sur des moteurs
différents. Ce document fixe le pattern à suivre pour interroger ces sources depuis une même
agence/API, sans jamais toucher au logiciel existant ni à son schéma applicatif. Il généralise
le pattern déjà en place dans ce dépôt pour CORE-SIM (`docs/backend/01-adapters-core-sim.md`,
`backend/solida/domain/ports/core_sim.py`).

## Principe directeur : un port par source, jamais un accès direct depuis le métier

Le domaine ne doit connaître qu'une interface abstraite (`Protocol` côté Python), jamais le
moteur SQL concret qui la sert. Une implémentation par moteur (`MySqlAgenceReader`,
`OracleAgenceReader`, `PostgresAgenceReader`, ...) traduit vers son propre dialecte. Le code
appelant ne voit jamais la différence entre les sources — exactement le rôle que joue
`CoreSimReader` aujourd'hui pour la base CORE-SIM.

## Ce qu'on a le droit de faire sans toucher au logiciel existant

- **Un rôle de lecture seule dédié**, créé par leur DBA, avec des `GRANT SELECT` ciblés — jamais
  un compte applicatif existant réutilisé. C'est le rôle `solida_lecteur` que ce projet utilise
  déjà pour CORE-SIM (`infra/postgres/coresim-init.sh`), vérifié par un `INSERT` réel refusé.
- **Des vues SQL côté leur base** : c'est la vraie zone de contrat stable à négocier avec eux.
  Une vue absorbe un changement de schéma interne (renommage de colonne, jointure historique
  compliquée) sans jamais casser le code appelant. C'est le point d'intégration à demander,
  jamais un accès brut aux tables internes.
- **Jamais de trigger, jamais d'écriture, jamais de modification de leur schéma applicatif** —
  seulement des objets en lecture ajoutés à côté.

## Ce qui change par moteur

- **Postgres** : `EXPLAIN ANALYZE` systématique sur toute requête nouvelle, index partiels sur
  les colonnes de filtre fréquentes, jamais `SELECT *` sur une vue large.
- **MySQL** : attention aux conversions implicites qui cassent un index (comparer `varchar` à
  `varchar`, jamais à un `int` casté) ; surveiller la colonne `type` d'`EXPLAIN` (`ALL` = scan
  complet à corriger).
- **Oracle** : toujours des bind variables (jamais de littéral dans le SQL, sinon chaque requête
  recompile son plan) ; attention aux conversions implicites de dates/fuseaux horaires.

## Règles communes, quel que soit le moteur

1. **Jamais de jointure cross-moteur** (pas de dblink/FDW improvisé entre deux moteurs
   différents) — le coût réseau et de sérialisation explose sans qu'on le voie venir. Toujours
   agréger côté applicatif : une requête par source, jointure en mémoire dans le code.
2. **Pagination par clé (keyset), jamais `OFFSET` profond** — un `OFFSET 50000` scanne quand même
   les 50 000 lignes avant de les jeter, sur les trois moteurs.
3. **Timeout court et circuit breaker par source** — si une source répond lentement, ça ne doit
   jamais bloquer les autres ni geler toute l'API. Un pool de connexions distinct par source,
   avec son propre timeout.
4. **Cache ou matérialisation pour ce qui ne bouge pas à la seconde** — le choix déjà fait dans
   ce projet pour les features de scoring (calculées à la demande depuis CORE-SIM, jamais de
   pipeline batch qui pourrait désynchroniser). Une vue matérialisée (si le moteur le permet) ou
   un cache applicatif à TTL court évite de retaper les mêmes jointures lourdes à chaque requête.
5. **Observabilité par source** : logguer la latence de chaque appel avec le nom de la source,
   pour savoir immédiatement laquelle ralentit un endpoint composite.
