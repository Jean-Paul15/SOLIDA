# Connectivité faible et connecteur de données réel

Ce fichier suit le même statut que `10-politique-credit-decisions-en-attente.md` et
`12-roles-et-organigramme-cef-mf.md` : ce qui suit n'est pas tranché, c'est un point de départ
documenté. Deux analyses croisées (une revue de prototype, puis une notation du dossier contre le
barème officiel du TDR) ont pointé le même écart sous deux angles — mode dégradé non construit,
et absence de connecteur vers un vrai logiciel de coopérative. Ce document vérifie ces deux
constats contre les sources primaires, et documente les décisions encore ouvertes plutôt que de
les trancher en silence.

## Sources vérifiées

- **TDR officiel** (`tdr-appel-a-candidatures-global-hackathon-cif-digicoop-wa-2026.pdf`, page 3) :
  barème confirmé — Pertinence 30 %, Originalité 20 %, **Faisabilité technique et réalisme du plan
  de développement 20 %**, Impact potentiel 15 %, Complémentarité de l'équipe 15 %. Pièce
  d'identité du chef d'équipe listée comme pièce obligatoire du dossier — à vérifier avant l'envoi,
  hors du périmètre que ce document peut contrôler.
- **Q&A officielle du hackathon** (`reponses-hackathon.pdf`, 24 pages lues intégralement) :
  - Q11.6 : *« la solution doit être opérationnelle sur un terminal standard (smartphone Android ou
    ordinateur sous Windows), prévoir un mode de fonctionnement dégradé en cas de faible
    connectivité et rester compatible avec des interfaces simples (fonctionnement hors ligne
    possible, USSD envisageable), avec des données locales. »*
  - Q17.3 : aucun serveur/hébergement/base fourni par la CIF pendant le hackathon — *« privilégiant
    une solution pouvant fonctionner localement sur ces postes et en mode dégradé, conformément aux
    contraintes et réalités opérationnelles des IMF »*.
  - **Nuance importante que les deux analyses n'ont pas relevée** : c'est phrasé « possible » /
    « envisageable », pas une obligation binaire de fonctionner 100 % hors ligne. La faisabilité
    technique est notée sur le **plan de développement**, pas uniquement sur du code déjà fini.
  - Sur le connecteur réel : Q6.1/Q6.2/Q6.4 confirment qu'un vrai logiciel existe par réseau
    national, et que plusieurs méthodes d'intégration sont envisageables (API, export, lecture
    seule). Mais **Q6.3, Q10.1 (question de l'utilisateur lui-même), Q12.3, Q16.1 et Q17.1
    confirment chacune, indépendamment, qu'aucune donnée réelle ne sera fournie aux équipes** —
    chaque équipe construit son propre jeu synthétique. Un connecteur vers un vrai système n'est
    donc **ni démontrable ni gradable pendant le hackathon** : il n'y a rien de réel à connecter.

## Ce qui est vérifié dans le code (au-delà de ce que les deux analyses ont vu)

| Constat | Preuve |
|---|---|
| Pas de batch/consolidation — features calculées à la demande contre CORE-SIM | `domain/ports/feature_store.py:8`, `adapters/core_sim/feature_store_core_sim.py` |
| Le motif `modele_enrichi_indisponible` documenté n'existe pas dans le code | `domain/values/motif_bascule.py` (4 motifs sur 5 de `04-cascade-et-cold-start.md:45`) ; un seul modèle (`ModeleConstant`) existe, la cascade bascule sur l'éligibilité du groupe, jamais sur une panne technique |
| `avertissements` toujours une constante générique, jamais un avertissement par feature manquante | `scorer_demande.py:312` (`AVERTISSEMENT_MODELE_SUBSTITUT`), malgré ce que documente `04-cascade-et-cold-start.md:81` |
| `date_dernier_rafraichissement` renvoie `date.today()` en dur | `feature_store_core_sim.py:114-115` — aucun indicateur de fraîcheur réel à afficher aujourd'hui |
| Frontend : aucun `error.tsx`/`loading.tsx`, aucune détection `navigator.onLine`, **zéro trace de `localStorage`/`sessionStorage`/`indexedDB`/lib offline** (recherche exhaustive sur `frontend/`, confirmée vide) | Un mode dégradé côté frontend part entièrement de zéro |
| `LecteurCoreSim` est un `Protocol` structurel à 9 méthodes de lecture pure, déjà substituable sans toucher au domaine | `domain/ports/core_sim.py` — **une vraie force à mettre en avant dans le dossier**, pas seulement une lacune |

## Tension non résolue à documenter, pas à trancher seul

`CLAUDE.md` §5 interdit `localStorage`/`sessionStorage` pour des données métier, et §8 pose la
souveraineté des données (elles ne quittent pas le périmètre de la coopérative) comme contrainte
permanente. Un vrai mode « file d'attente locale, saisie hors ligne, synchronisation au retour du
réseau » suppose de persister des données métier (montant demandé, identifiant du sociétaire,
revenu déclaré) sur l'appareil de l'agent — en tension directe avec ces deux règles. Ce n'est pas
un détail : c'est une décision d'architecture et de gouvernance, pas quelque chose à trancher
silencieusement dans le code.

## Partie 1 — Mode dégradé / faible connectivité : trois niveaux d'ambition

Présentés sans trancher lequel construire — c'est un choix produit, pas technique.

1. **Dégradation propre côté serveur.** Remplacer les exceptions non rattrapées (CORE-SIM
   injoignable, échec du modèle) par des erreurs domaine explicites, dans l'esprit de
   `DonneesInsuffisantes` déjà existante — ferme l'écart déjà identifié cette session (scénario 4
   du repli en cas de panne). Aucun stockage client, aucune tension avec `CLAUDE.md`. Le plus sûr,
   le plus rapide à construire.
2. **Cache de référentiel non sensible côté frontend.** Grille de crédit, catalogue de produits —
   jamais de donnée sur un sociétaire précis. Réduit la dépendance réseau de l'interface sans
   jamais stocker de donnée personnelle sur l'appareil. Compatible avec `CLAUDE.md` tel quel.
3. **File d'attente locale de demandes de scoring.** Répond le plus fidèlement à Q11.6/Q17.3, mais
   suppose de persister des données métier sur l'appareil — nécessite une exception explicite et
   assumée à `CLAUDE.md` §5/§8. Questions non tranchées, à arbitrer avant toute construction :
   - Combien de temps une copie locale reste-t-elle valable ?
   - Une décision prise hors ligne peut-elle être confirmée sans re-vérification serveur ?
   - Comment auditer une action effectuée hors connexion ?
   - Comment résoudre un conflit au retour du réseau (ex. deux agents, même sociétaire) ?

**Recommandation non appliquée** : construire (1) et (2) avant le hackathon — peu de risque,
referme un vrai écart technique déjà démontré par ce document. Documenter (3) comme trajectoire
post-hackathon nécessitant un arbitrage produit explicite, pas un design silencieux.

## Partie 2 — Connecteur de données réel

Rien de réel n'est démontrable pendant le hackathon (aucune donnée réelle fournie, confirmé cinq
fois indépendamment dans la Q&A) — ce n'est donc pas le chantier prioritaire pour la notation,
contrairement à ce que suggérait la première analyse.

**Force déjà en place** : `LecteurCoreSim` (`domain/ports/core_sim.py`) est un port structurel à 9
méthodes, déjà substituable sans toucher au domaine — brancher un vrai connecteur plus tard
n'exige qu'une nouvelle classe qui respecte ce contrat. À valoriser dans le dossier.

**Stratégie cible à documenter** (alignée sur Q6.2, « envisagez toutes ces méthodes ») : API en
lecture seule comme connexion principale, export CSV / dépôt SFTP en secours. Sans construire de
code maintenant — seulement documenter le contrat cible et les inconnues à trancher avec une
coopérative pilote réelle, pas en interne :
- correspondance entre les champs du logiciel réel et le schéma SOLIDA ;
- mécanisme d'import/synchronisation et sa fréquence ;
- indicateur fiable de fraîcheur des données (aujourd'hui factice, voir tableau ci-dessus) ;
- gestion des données invalides ou incomplètes ;
- reprise après coupure et stratégie de réconciliation.

## Partie 3 — Corrections recommandées à la note de présentation

À appliquer manuellement (source du PDF non identifiée dans ce dépôt — probablement à reconstruire
avant correction) :

1. Le modèle EBM est présenté comme entraîné ; le code utilise aujourd'hui `ModeleConstant`
   (probabilité fixe, `adapters/ml/modele_constant.py:6`).
2. Un traitement nocturne / une table de référence par sociétaire est annoncé ; aucun batch
   n'existe, le calcul est fait à la demande (voir tableau ci-dessus).
3. « Toute coopérative alimente SOLIDA par un simple export » : aucun import CSV ni connecteur
   générique n'existe. Formulation corrigée proposée : *« SOLIDA définit le contrat cible ; le
   connecteur d'import sera adapté au format fourni par la coopérative pilote. »*
4. « Aucune connexion permanente » est trop affirmatif : l'interface dépend toujours de l'API en
   direct, aucun cache réel n'existe aujourd'hui.

## Partie 4 — Point administratif

La copie de la pièce d'identité du chef d'équipe est listée comme pièce obligatoire du dossier de
candidature (TDR, page 3). Sa présence dans l'envoi final n'a pas pu être vérifiée depuis ce
dépôt — à confirmer avant la clôture des inscriptions (23/08/2026, 23h59 GMT+0).
