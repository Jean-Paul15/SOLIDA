# Monitoring sécurité — applicatif et infrastructure

Ce document couvre la sécurité et la disponibilité de l'application et de son infrastructure
(authentification, accès aux données, intégrité du journal d'audit). Le monitoring du **modèle**
(dérive des décisions de scoring, calibration de la grille) est un sujet distinct, non couvert
ici — amorcé par l'immutabilité de `pdo`/`score_reference`/`odds_reference` (voir
`03-decisions-provisoires-a-revoir.md`), développement futur séparé.

## Ce qui est surveillé aujourd'hui

Tout passe par `journal_audit` (table unique, en insertion seule — voir plus bas), écrit via
`JournalAuditSql.enregistrer_evenement`. Types d'événements existants :

| Type | Où | Ce qu'il capture |
|---|---|---|
| `connexion_reussie` / `connexion_echouee` | `routeurs/auth.py` | identifiant, IP réelle, navigateur |
| `deconnexion` | `routeurs/auth.py` | IP réelle, navigateur |
| `mot_de_passe_change` | `routeurs/auth.py` | IP réelle, navigateur |
| `recherche_societaires` | `societaires.py` | acteur, terme, nombre de résultats, IP réelle, navigateur |
| `consultation_dossier` | `societaires.py` | acteur, sociétaire consulté, IP réelle, navigateur |
| `scoring_previsualise` / `scoring_confirme` | `scorer_demande.py` | acteur, sociétaire |
| `fiche_archivee` | `archiver_fiche.py` | acteur, décision archivée |
| `alerte_volume_lecture` | `detecter_lectures_anormales.py` (nouveau) | acteur, volume constaté, seuil |

Le verrou de connexion (`routeurs/auth.py`, 5 échecs / 15 min) est indexé sur `identifiant + IP
réelle` depuis le round 3 du pentest — pas l'identifiant seul, pour qu'un anonyme ne puisse pas
verrouiller un compte connu sans jamais avoir de mot de passe correct. L'IP réelle est restaurée
derrière le tunnel Cloudflare par le module `realip` de nginx (`infra/nginx/nginx.conf`), qui ne
fait confiance à `CF-Connecting-IP` que si la connexion vient du tunnel local ou du réseau
Docker — jamais depuis n'importe où.

## Détection d'un volume de lecture hors norme

`backend/solida/batch/jobs/detecter_lectures_anormales.py` — compte, par acteur, les événements
`recherche_societaires` + `consultation_dossier` sur une fenêtre glissante d'1 heure ; au-delà de
100 lectures cumulées, écrit une entrée `alerte_volume_lecture`.

**Recherche faite avant de concevoir ce mécanisme** (protocole CLAUDE.md §2) : la pratique
reconnue en détection d'exfiltration (UEBA — Sumo Logic, Exabeam, Microsoft Sentinel, IBM)
déconseille un seuil fixe qui bloque automatiquement — risque de faux positifs (une journée
chargée légitime) et le seuil devient lui-même un vecteur de déni de service (faire bloquer un
agent légitime exprès en générant artificiellement du volume sur son compte). D'où le choix,
confirmé avec le commanditaire : **alerte + décision humaine**, jamais de blocage automatique.
Un superviseur ou administrateur qui juge une alerte réellement anormale utilise le blocage
déjà existant :

```
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes bloquer \
    --identifiant <identifiant>
docker compose run --rm api python -m solida.infrastructure.cli_provisionner_comptes lister-bloques
```

**Ce que ce mécanisme ne détecte pas** : un vol "lent", étalé sous le seuil sur la durée, ne
déclenche rien. C'est une limite connue, pas cachée — fermer ce cas demanderait une vraie
baseline de comportement par acteur (ce que fait un UEBA complet), disproportionné pour
l'échelle de SOLIDA aujourd'hui (voir « Ce qui est explicitement laissé de côté » plus bas).

**Le seuil (100 lectures/heure)** est repris tel quel de la recommandation du rapport de pentest
round 3, pas inventé pour l'occasion — même logique que le plafond de pagination du finding F22
(round précédent). Marqué comme ajustable dans
`03-MODELE/10-politique-credit-decisions-en-attente.md` : la vraie valeur dépend du volume réel
observé une fois l'application utilisée en production, pas d'une intuition.

**Le navigateur (User-Agent)** est désormais capturé sur `recherche_societaires` et
`consultation_dossier`, comme il l'était déjà pour les événements d'authentification. C'est un
indice de contexte pour la personne qui revoit une alerte ("ces requêtes sortent toutes avec
`curl/8.x`, ça vaut le coup de regarder") — **jamais un critère de blocage automatique** : un
User-Agent se falsifie en une ligne (`curl -H "User-Agent: ..."`), un abuseur un minimum
sérieux le fera systématiquement.

**Pourquoi pas un chiffrement du payload / une liaison au client officiel ?** Question posée
explicitement par le commanditaire, recherche faite (OWASP API1:2023 — Broken Object Level
Authorization) : ce n'est pas le bon outil. Un agent authentifié via une session valide a, par
définition, tout ce qu'il faut pour reproduire ce que ferait l'interface — chiffrer le corps de
la requête ne change rien, puisque la logique de déchiffrement devrait de toute façon être
livrée dans le JavaScript envoyé au navigateur, donc lisible par quiconque l'inspecte. La vraie
protection contre l'accès non autorisé est le cloisonnement par agence côté serveur (déjà en
place, vérifié par le pentest round 3 : 0 fuite hors agence) ; ce qui manquait était la
**détection** d'un usage massif mais autorisé, pas une barrière d'accès supplémentaire — d'où ce
mécanisme plutôt qu'une couche de chiffrement.

## Intégrité du journal d'audit

`journal_audit` est en insertion seule depuis la migration `47717ebe5930` : un trigger
(`journal_audit_insertion_seule`, même patron que `decision_scoring_insertion_seule`) bloque
tout `UPDATE`/`DELETE`, y compris pour `solida_app` (le rôle applicatif normal). Seule
exception : une transaction connectée avec le rôle dédié `solida_purge`, qui pose explicitement
le flag de session attendu par le trigger (`SET LOCAL solida.purge_audit = 'on'`) — c'est
exactement ce que fait `purger_journal_audit.py`, seul appelant légitime, pour la purge par
rétention (1 an, déjà en place).

**Pourquoi un trigger et pas un simple `REVOKE`** : `solida_app` est propriétaire de la table
(elle l'a créée via les migrations) — en PostgreSQL, un propriétaire contourne toujours les
`GRANT`/`REVOKE`. Seul un trigger bloque réellement tout le monde, propriétaire compris.
Confirmé par la pratique établie (wiki PostgreSQL « Audit trigger »).

**Limite honnête de cette protection** : ce trigger est un vrai obstacle contre une erreur
applicative, un bug, ou une tentative via une faille non encore trouvée — **pas** une garantie
absolue contre quelqu'un qui obtiendrait un accès direct aux identifiants `solida_app` (ce
scénario suppose déjà une compromission bien plus grave que ce dont il est question ici : accès
direct à la base de production). Une protection plus forte existe et n'est pas construite ici :
un chaînage de hachage (chaque ligne inclut le hachage de la précédente), qui rend toute
altération *détectable* même par quelqu'un avec un accès direct suffisant, plutôt que de
seulement la bloquer. Disproportionné pour l'échelle actuelle de SOLIDA — piste future, pas un
manque caché.

## Comptes bloqués — visibilité admin

`bloquer_compte`/`debloquer_compte` restent **volontairement CLI-only**, choix de sécurité
délibéré déjà en place avant ce travail (« surface d'attaque nulle sur la gestion des comptes »,
`cli_provisionner_comptes.py`) : décision confirmée, pas remise en cause. Un administrateur
consulte les comptes désactivés via `lister-bloques` (CLI, lecture seule, ajouté ici) — pas via
un endpoint HTTP, pour ne pas rouvrir de surface que le code évitait déjà délibérément.

## Ce qui est explicitement laissé de côté (et pourquoi)

- **UEBA / apprentissage de comportement complet** (baseline par acteur sur plusieurs mois) :
  disproportionné pour le volume de SOLIDA (une coopérative, quelques dizaines d'agents) — un
  seuil simple et une revue humaine suffisent à ce stade.
- **Chaînage de hachage sur `journal_audit`** : protection plus forte que le trigger actuel,
  mais complexité et coût de maintenance non justifiés tant qu'aucun incident réel ne l'exige.
- **Endpoint HTTP de gestion des comptes** (lister, bloquer, débloquer) : délibérément absent,
  cohérent avec le choix déjà fait dans le code avant ce travail.
- **Blocage automatique sur dépassement de seuil** : écarté explicitement (risque de faux
  positifs et de déni de service), voir plus haut.

## Ancrage réglementaire

La loi togolaise n°2019-014 sur la protection des données à caractère personnel ne fixe pas de
mandat technique précis pour la détection d'accès anormal ou l'intégrité d'un journal de
sécurité (même constat déjà fait pour sa politique de rétention, voir
`03-decisions-provisoires-a-revoir.md`). Ce qui est fait ici s'aligne avec les principes
largement reconnus en la matière (traçabilité, moindre privilège, détection d'accès anormal —
OWASP, pratique UEBA établie), pas avec une certification togolaise spécifique qui n'existe pas
pour ce contexte.
