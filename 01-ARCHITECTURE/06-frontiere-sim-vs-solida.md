# La frontière CORE-SIM / SOLIDA

**C'est la décision structurante du projet.** Elle est ce qui rend crédible, devant le jury, notre
affirmation que SOLIDA se déploie dans une coopérative existante sans refonte de son système
d'information. Si le code confond les deux, l'affirmation devient un slogan invérifiable.

---

## Les deux systèmes

### CORE-SIM — le système de gestion simulé

Ce que nous simulons, c'est **le logiciel de gestion que la coopérative possède déjà** : sociétaires,
comptes d'épargne, mouvements, groupes de caution, garanties, demandes, crédits, échéanciers,
remboursements.

Dans la vraie vie, ce système appartient à l'IMF. Nous ne l'écrivons pas, nous ne le modifions pas,
nous ne l'exploitons pas. Nous ne faisons que **lire dedans**.

Pendant le hackathon, il est produit par le simulateur (bloc A) et vit dans une base PostgreSQL
nommée `coresim`.

### SOLIDA — notre produit

Ce que nous construisons : les agrégats de la couche solidaire, le feature store, les modèles,
les scores produits, les fiches de justification, le registre d'audit, les utilisateurs et leurs
rôles, les paramètres de la grille et du moteur de crédit progressif.

Vit dans une base PostgreSQL distincte nommée `solida`.

---

## Ce que la frontière impose

| Règle | Mise en œuvre technique |
|---|---|
| SOLIDA ne modifie jamais CORE-SIM | Utilisateur PostgreSQL `solida_lecteur` avec `GRANT SELECT` uniquement |
| Aucune jointure SQL entre les deux bases | Deux connexions distinctes, pas de FDW, pas de `dblink` |
| Un seul point d'accès | Tout passe par le port `LecteurCoreSim` et son unique adaptateur |
| Le domaine ignore le schéma de CORE-SIM | L'adaptateur traduit les colonnes SQL en entités métier |
| Les données utiles sont copiées, pas référencées | Le feature store contient des valeurs, pas des pointeurs |

**Vérification mécanique :** un test d'intégration tente une écriture dans `coresim` avec les
identifiants de SOLIDA et **doit échouer**. Si ce test passe, la configuration est fausse.

---

## Pourquoi copier plutôt que joindre

Une jointure directe serait plus simple à court terme. Elle est refusée pour trois raisons :

1. **Le vrai SI ne sera pas PostgreSQL.** Il peut être SQL Server, Oracle, un logiciel propriétaire
   avec export CSV quotidien, voire une API. Un code qui suppose une base joignable ne se déploie
   nulle part.
2. **Le batch doit pouvoir tourner à froid.** Le rafraîchissement nocturne lit CORE-SIM une fois et
   travaille ensuite sur ses propres données. Sans copie, chaque scoring rejouerait des requêtes
   lourdes sur le système de production de l'IMF, en pleine journée.
3. **La reproductibilité.** Un score doit pouvoir être rejoué à l'identique six mois plus tard.
   Cela suppose de conserver les valeurs telles qu'elles étaient au moment de la décision.

---

## Les deux chemins de données

### Chemin différé (batch, nocturne ou hebdomadaire)

```
CORE-SIM
   │  lecture seule, en masse
   ▼
LecteurCoreSim (adaptateur)
   │
   ▼
Entités du domaine
   │
   ├──► CalculateurFeaturesIndividuelles ──┐
   │                                        │
   └──► CalculateurAgregatsSolidaires ──► AgregatsGroupe ──┤
                                            │
                                            ▼
                                    FeatureStore (base SOLIDA)
```

Ce chemin est le seul à toucher CORE-SIM en volume. Il tourne hors heures d'ouverture.

### Chemin immédiat (guichet, temps de réponse < 1 s)

```
Agent saisit : montant, durée, objet (+ actualisation éventuelle)
   │
   ▼
EntreeScoring
   │
   ▼
FeatureStore (base SOLIDA)  ──► features pré-calculées du sociétaire
   │
   ▼
Cascade → Modèle → Calibration → Scorecard → Grille
   │
   ▼
ResultatScoring ──► JournalAudit (base SOLIDA)
```

**Ce chemin ne touche jamais CORE-SIM.** C'est ce qui garantit le temps de réponse et l'absence
d'impact sur le système de production de la coopérative.

Seule exception admise : la recherche de sociétaire par nom, qui peut interroger CORE-SIM en
lecture légère, ou consulter un index local rafraîchi par le batch. Décision : **index local**,
pour ne dépendre de rien au guichet.

---

## Ce que change le passage au réel

Le jour où une coopérative pilote branche son vrai système, voici exactement ce qui bouge :

| Élément | Change ? |
|---|---|
| `adapters/core_sim/lecteur_postgres.py` | **Remplacé** par un nouvel adaptateur |
| Le port `LecteurCoreSim` | Non |
| Le domaine | Non |
| Les features | Non, sauf si un champ manque |
| Les modèles | Recalibrés, pas réécrits |
| Le front | Non |
| Le simulateur | Devient inutile, conservé pour les tests |

**Un seul fichier.** C'est l'argument de déployabilité, rendu vérifiable.

---

## Le contrat d'intégration

Le port `LecteurCoreSim` définit implicitement l'ensemble minimal de données qu'une IMF doit
pouvoir exposer. Ce périmètre est formalisé dans `02-DONNEES/04-contrat-integration.md` et
constitue notre proposition de standard d'interopérabilité pour le réseau CIF.

Trois modes d'intégration sont prévus, par ordre de préférence :

1. **Vue en lecture seule** dans la base du SI de l'IMF, exposant les champs du contrat.
2. **Export périodique** (CSV ou Parquet) déposé dans un répertoire, ingéré par le batch.
3. **API** exposée par le SI, si l'éditeur en fournit une.

Le mode 2 est le plus universel : aucune IMF ne refuse un export, alors que beaucoup refusent un
accès direct à leur base.
