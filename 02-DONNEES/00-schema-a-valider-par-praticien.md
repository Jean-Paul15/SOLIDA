# SOLIDA — Schéma de données pour génération synthétique

**Document de travail v1.0 — à faire valider par un professionnel exerçant en institution de microfinance**

Hackathon National d'Innovation CIF / DigiCoop-WA+ — Thématique 02, Scoring Microcrédit

---

## 1. Objet de ce document

Ce document décrit **la structure de données que nous prévoyons de générer** pour entraîner et démontrer le système de scoring SOLIDA. Il ne s'agit pas encore du générateur lui-même, mais du plan de données à valider avant de coder.

**Ce que nous cherchons à faire confirmer par un praticien du secteur :**

1. Ces tables et ces champs existent-ils réellement dans le système de gestion d'une coopérative financière togolaise ?
2. Quels champs sont réellement renseignés en pratique, et lesquels restent souvent vides ?
3. Quels champs manquent, que nous n'avons pas anticipés ?
4. Les ordres de grandeur et proportions proposés sont-ils réalistes ?

Chaque section comporte un bloc **[À VALIDER]** signalant les points sur lesquels l'avis du praticien est déterminant.

---

## 2. Vue d'ensemble

### 2.1 Nombre de tables

Le générateur produira **13 tables**, réparties en quatre familles.

| Famille | Tables | Rôle |
|---|---|---|
| Référentiels | `agence`, `agent_credit`, `produit_credit` | Contexte institutionnel |
| Sociétaires | `societaire`, `compte_epargne`, `mouvement_epargne` | Profil et comportement individuel |
| Solidaire (segment) | `groupe_caution`, `appartenance_groupe`, `garantie` | Crédits de groupe uniquement — minoritaires, le crédit individuel adossé à l'épargne domine |
| Crédit | `demande_credit`, `credit`, `echeance`, `remboursement` | Cycle de vie du crédit et variable cible |

À ces 13 tables s'ajoutent **2 tables dérivées** (`feature_individuelle`, `feature_solidaire`), non générées mais calculées par le traitement batch, décrites en section 8.

### 2.2 Volumétrie cible

Périmètre simulé : **une coopérative financière de taille moyenne, observée sur 5 ans** (2021-2026).

| Table | Lignes estimées | Commentaire |
|---|---|---|
| `agence` | 8 | Réseau régional |
| `agent_credit` | 45 | 4 à 8 agents par agence |
| `produit_credit` | 6 | Individuel, solidaire, agricole, commerce, urgence, équipement |
| `societaire` | 25 000 | Base membres |
| `compte_epargne` | 27 000 | Certains membres ont 2 comptes |
| `mouvement_epargne` | ~900 000 | 24 mois d'historique, ~1,4 mouvement/mois/compte actif |
| `groupe_caution` | ~400 | Segment des groupements (GIE), minoritaire |
| `appartenance_groupe` | ~4 900 | Historique inclus (entrées/sorties) |
| `garantie` | 22 000 | Majoritairement `epargne_nantie` ; `caution_solidaire_gie` en segment |
| `demande_credit` | 34 000 | Inclut les demandes refusées |
| `credit` | 28 500 | Demandes acceptées |
| `echeance` | ~285 000 | ~10 échéances par crédit en moyenne |
| `remboursement` | ~270 000 | Paiements réels, y compris partiels et tardifs |

**Total : environ 1,6 million de lignes**, dominé par les tables de mouvements. Format de sortie prévu : Parquet (ou CSV si contrainte d'outillage), taille estimée 80 à 150 Mo.

> **[À VALIDER]** — Ces volumes correspondent-ils à une coopérative togolaise réaliste ? Faut-il viser plus petit (caisse locale) ou plus grand (réseau) ?

---

## 3. Référentiels

### 3.1 `agence`

| Champ | Type | Description |
|---|---|---|
| `agence_id` | PK, string | Identifiant |
| `nom` | string | Libellé |
| `zone` | enum | `urbain`, `semi_urbain`, `rural` |
| `region` | string | Région administrative |
| `date_ouverture` | date | |

**Génération :** 3 agences urbaines (Lomé), 3 semi-urbaines, 2 rurales.

### 3.2 `agent_credit`

| Champ | Type | Description |
|---|---|---|
| `agent_id` | PK, string | |
| `agence_id` | FK | |
| `date_embauche` | date | |
| `anciennete_mois` | int | Dérivé |
| `portefeuille_max` | int | Nombre de dossiers suivis |

**Utilité pour le projet :** permet de démontrer l'hétérogénéité des décisions entre agents, qui est l'un des problèmes que SOLIDA prétend résoudre. Sans cette table, l'argument reste théorique.

> **[À VALIDER]** — L'identifiant de l'agent instructeur est-il effectivement enregistré sur chaque dossier de crédit ?

### 3.3 `produit_credit`

| Champ | Type | Description |
|---|---|---|
| `produit_id` | PK, string | |
| `libelle` | string | |
| `type_garantie` | enum | `solidaire`, `individuelle_materielle`, `epargne_nantie`, `caution_morale` |
| `montant_min`, `montant_max` | int (FCFA) | |
| `duree_min_mois`, `duree_max_mois` | int | |
| `taux_annuel` | float | TAEG appliqué |

**Génération :** taux entre 18 % et 24 %, plafonnés à **24 % TAEG**, nouveau taux d'usure applicable aux SFD de l'UEMOA depuis le 1er juin 2026 (auparavant 27 % au Togo).

---

## 4. Sociétaires

### 4.1 `societaire`

| Champ | Type | Description | Utilisé par le modèle |
|---|---|---|---|
| `societaire_id` | PK, string | | non (clé) |
| `agence_id` | FK | Agence de rattachement | indirect |
| `segment` | enum | salarié, individuel, jeune, femme_gie, agricole — produit souscrit, disponible dès l'adhésion | oui |
| `date_adhesion` | date | Entrée en sociétariat **= début de la relation d'épargne** | oui (ancienneté, trajectoire d'épargne) |
| `date_naissance` | date | | oui (âge) |
| `sexe` | enum | `F`, `M` | **non — exclu du modèle** |
| `situation_matrimoniale` | enum | célibataire, marié(e), veuf(ve), divorcé(e) | à discuter |
| `nb_personnes_a_charge` | int | | oui |
| `niveau_instruction` | enum | aucun, primaire, secondaire, supérieur | à discuter |
| `zone_residence` | enum | urbain, semi_urbain, rural | oui |
| `secteur_activite` | enum | commerce, agriculture, artisanat, services, transport, élevage, salarié, autre | oui |
| `anciennete_activite_mois` | int | Depuis quand exerce-t-il | oui |
| `revenu_mensuel_declare` | int (FCFA) | Déclaratif, recueilli à l'entretien | oui |
| `charges_mensuelles_declarees` | int (FCFA) | | oui |
| `possede_local_commercial` | bool | Propriétaire / locataire / ambulant | oui |
| `statut_logement` | enum | propriétaire, locataire, hébergé | à discuter |
| `parts_sociales_montant` | int (FCFA) | Capital souscrit dans la coopérative | oui |
| `statut` | enum | actif, inactif, radié | filtre |

> **[À VALIDER — point le plus important de ce document]**
> - Le revenu déclaré est-il systématiquement saisi, ou reste-t-il souvent vide ?
> - Les charges mensuelles sont-elles réellement collectées ?
> - Existe-t-il un champ de notation qualitative de l'agent après visite terrain (viabilité de l'activité, moralité, tenue du commerce) ? La littérature le donne comme prédictif, mais c'est rarement un champ structuré dans un SI de microfinance. **Nous le laissons désactivé par défaut (ADR-017)** : il n'entre dans le modèle que si sa saisie structurée est confirmée.
> - Le niveau d'instruction et la situation matrimoniale sont-ils collectés au KYC ?

**Note d'éthique :** `sexe` est généré pour réalisme démographique mais **exclu des variables du modèle**, conformément au principe de non-discrimination annoncé dans notre note de présentation. Il servira uniquement à contrôler *a posteriori* qu'aucune variable retenue n'en constitue un substitut.

### 4.2 `compte_epargne`

| Champ | Type | Description |
|---|---|---|
| `compte_id` | PK, string | |
| `societaire_id` | FK | |
| `type_compte` | enum | `dav` (dépôt à vue), `plan_epargne`, `depot_terme`, `epargne_nantie` |
| `date_ouverture` | date | |
| `solde_actuel` | int (FCFA) | |
| `statut` | enum | actif, dormant, clos |

### 4.3 `mouvement_epargne`

| Champ | Type | Description |
|---|---|---|
| `mouvement_id` | PK, string | |
| `compte_id` | FK | |
| `date_operation` | date | |
| `sens` | enum | `depot`, `retrait` |
| `montant` | int (FCFA) | |
| `canal` | enum | guichet, agent_terrain, mobile | à valider |

**Pourquoi cette table est essentielle :** elle porte le signal le plus exploitable du comportement financier d'un membre. La régularité des dépôts, plus que leur montant, est un indicateur reconnu de discipline financière. C'est aussi ce qui permet de scorer un nouvel emprunteur qui n'a pas encore d'historique de crédit.

> **[À VALIDER]** — L'historique des mouvements est-il conservé sur combien d'années ? Le canal de l'opération est-il tracé ?

---

## 5. Bloc solidaire (segment des crédits de groupe)

**Ce bloc ne concerne qu'une minorité du portefeuille.** Dans le modèle mutualiste, le crédit est
majoritairement individuel et adossé à l'épargne nantie du sociétaire (bloc 4). Les tables
ci-dessous ne s'appliquent qu'au segment des groupements (GIE), typiquement les groupements de
femmes. Aucune structure de graphe n'est construite : ces tables alimentent des agrégats simples
(taux de remboursement du groupe, taille), voir `01-ARCHITECTURE/07`.

### 5.1 `groupe_caution`

| Champ | Type | Description |
|---|---|---|
| `groupe_id` | PK, string | |
| `agence_id` | FK | |
| `nom_groupe` | string | |
| `date_creation` | date | |
| `taille_actuelle` | int | Nombre de membres actifs |
| `statut` | enum | actif, dissous, en_difficulte |
| `nb_cycles_completes` | int | Cycles de crédit menés à terme |

**Génération :** taille des groupes entre 3 et 20 membres, mode autour de 5 à 8. Les groupes sont constitués au sein d'une même agence et d'une même zone géographique.

### 5.2 `appartenance_groupe`

Table de liaison, avec historique.

| Champ | Type | Description |
|---|---|---|
| `appartenance_id` | PK, string | |
| `groupe_id` | FK | |
| `societaire_id` | FK | |
| `date_entree` | date | |
| `date_sortie` | date, nullable | Null si toujours membre |
| `role` | enum | membre, président, trésorier, secrétaire |

**Pourquoi conserver l'historique des sorties :** un groupe qui perd régulièrement des membres est un signal de fragilité que la seule photographie actuelle ne capterait pas.

### 5.3 `garantie`

**Table pivot : elle distingue la garantie réelle (épargne nantie), majoritaire, du crédit de
groupe (caution solidaire GIE), minoritaire.**

| Champ | Type | Description |
|---|---|---|
| `garantie_id` | PK, string | |
| `credit_id` | FK | Crédit garanti |
| `garant_societaire_id` | FK, nullable | Rempli seulement pour `caution_solidaire_gie` |
| `beneficiaire_societaire_id` | FK | Pour qui |
| `type_garantie` | enum | `epargne_nantie` (majoritaire), `caution_solidaire_gie` (segment groupe) |
| `montant_garanti` | int (FCFA) | |
| `date_engagement` | date | |
| `garantie_appelee` | bool | La garantie a-t-elle été mise en jeu |

> **[À VALIDER — deuxième point critique, celui qui calibre toute la couche solidaire]**
> - Quelle est la part réelle du portefeuille en crédit de groupe / caution solidaire, par rapport au crédit individuel adossé à l'épargne ?
> - Le fait qu'une garantie ait été **appelée** est-il tracé dans le système ? C'est le signal le plus fort de la couche solidaire, mais nous ne savons pas s'il est saisi.
> - Les cautions individuelles hors groupe (une personne nommément garante d'une autre) existent-elles dans votre réseau, et sont-elles enregistrées de façon structurée ?

---

## 6. Cycle de crédit

### 6.1 `demande_credit`

Table pivot du scoring : **c'est l'objet que le modèle prend en entrée**.

| Champ | Type | Description |
|---|---|---|
| `demande_id` | PK, string | |
| `societaire_id` | FK | |
| `agence_id` | FK | |
| `agent_id` | FK | Agent instructeur |
| `produit_id` | FK | |
| `groupe_id` | FK, nullable | Null si demande individuelle |
| `date_demande` | date | |
| `montant_demande` | int (FCFA) | |
| `duree_demandee_mois` | int | |
| `objet_credit` | enum | fonds_roulement, equipement, intrants_agricoles, stock, urgence_sante, scolarite, habitat, autre |
| `date_decision` | date | Permet de mesurer le délai d'instruction |
| `decision` | enum | accorde, accorde_partiel, refuse, abandonne |
| `montant_accorde` | int, nullable | |
| `motif_refus` | enum, nullable | À valider |

**Le fait d'inclure les demandes refusées est délibéré.** Cela permet de mesurer le délai d'instruction réel et l'hétérogénéité entre agents. En revanche, cela pose le problème classique du **biais de sélection** : on ne connaît jamais le comportement de remboursement des dossiers refusés, ce qui biaise l'apprentissage. Nous l'aborderons par une pondération, et nous le documenterons explicitement plutôt que de le passer sous silence.

> **[À VALIDER]** — Les demandes refusées sont-elles conservées dans le système, ou seuls les crédits accordés sont-ils enregistrés ? La réponse change la stratégie de modélisation.

### 6.2 `credit`

| Champ | Type | Description |
|---|---|---|
| `credit_id` | PK, string | |
| `demande_id` | FK | |
| `societaire_id` | FK | |
| `montant_octroye` | int (FCFA) | |
| `taux_annuel` | float | |
| `duree_mois` | int | |
| `periodicite` | enum | hebdomadaire, bimensuelle, mensuelle, in_fine |
| `date_deblocage` | date | |
| `date_echeance_finale` | date | |
| `numero_cycle` | int | Rang du crédit pour ce sociétaire (1er, 2e, 3e…) |
| `statut` | enum | en_cours, solde, en_souffrance, radie, restructure |
| `capital_restant_du` | int (FCFA) | |

Le champ `numero_cycle` matérialise le **crédit progressif** : montants croissants au fil des cycles réussis.

### 6.3 `echeance`

| Champ | Type | Description |
|---|---|---|
| `echeance_id` | PK, string | |
| `credit_id` | FK | |
| `numero_echeance` | int | |
| `date_echeance_prevue` | date | |
| `montant_capital` | int | |
| `montant_interet` | int | |
| `montant_total_du` | int | |
| `statut` | enum | payee, partielle, impayee, a_venir |

### 6.4 `remboursement`

| Champ | Type | Description |
|---|---|---|
| `remboursement_id` | PK, string | |
| `echeance_id` | FK | |
| `credit_id` | FK | |
| `date_paiement` | date | |
| `montant_paye` | int (FCFA) | |
| `jours_retard` | int | Dérivé : date_paiement − date_echeance_prevue |
| `paye_par_garant` | bool | La caution a-t-elle payé à la place du débiteur |

Le champ `paye_par_garant` est important : il matérialise le fonctionnement réel de la caution solidaire et alimente la variable la plus parlante de la couche solidaire (« ce membre a déjà été sauvé par son groupe »).

> **[À VALIDER]** — Le système distingue-t-il un remboursement effectué par le débiteur d'un remboursement effectué par le groupe ou le garant ?

---

## 7. Variable cible (le label)

**Définition proposée :** un crédit est considéré en **défaut** si au moins une échéance présente un retard supérieur à **90 jours** au cours de la vie du crédit.

Cette définition s'aligne sur la notion de créance en souffrance utilisée dans le suivi prudentiel des SFD de l'UEMOA, mais **elle doit être confirmée**, notamment pour le crédit agricole où des délais plus longs sont parfois admis compte tenu de la saisonnalité.

**Variantes à tester :** PAR30 (retard > 30 jours), PAR60, PAR90. Nous retiendrons celle qui correspond à la pratique effective de l'institution.

> **[À VALIDER — troisième point critique]**
> - Quel seuil de retard déclenche le classement en créance en souffrance dans votre institution ?
> - Ce seuil est-il différent pour le crédit agricole ?
> - Un crédit restructuré est-il compté comme défaut ?

---

## 8. Variables dérivées calculées en batch

Tables `feature_individuelle` et `feature_solidaire` (voir `02-DONNEES/02-schema-solida.md`),
**non générées** mais calculées par le traitement nocturne décrit dans notre note de présentation.
Une ligne par sociétaire et par date de référence, rafraîchie périodiquement.

### 8.1 Variables individuelles agrégées

| Variable | Calcul |
|---|---|
| `anciennete_societaire_mois` | Depuis `date_adhesion` |
| `solde_epargne_moyen_6m` | Moyenne mobile sur `mouvement_epargne` |
| `nb_mois_avec_depot_12m` | Régularité de l'épargne (0 à 12) |
| `tendance_epargne_12m` | Solde en hausse / stable / en érosion sur 12 mois |
| `volatilite_epargne` | Écart-type des soldes mensuels |
| `ratio_epargne_revenu` | Effort d'épargne : solde moyen / revenu déclaré |
| `anciennete_epargne_mois` | Depuis `date_adhesion`, à la date de la demande — signal disponible même pour un primo-emprunteur |
| `ratio_endettement` | Échéance mensuelle / revenu net déclaré |
| `nb_credits_anterieurs` | Comptage sur `credit` |
| `nb_incidents_anterieurs` | Comptage des retards > seuil |
| `max_jours_retard_historique` | Pire retard observé |
| `montant_max_rembourse` | Plus gros crédit mené à terme |

### 8.2 Variables de la couche solidaire (segment de groupe uniquement)

Calculées uniquement pour les sociétaires du segment `femme_gie` ; `null` pour tous les autres
(majorité du portefeuille), voir `01-ARCHITECTURE/07` pour la justification de ce périmètre restreint.

| Variable | Calcul |
|---|---|
| `en_groupe` | Le sociétaire appartient-il à un groupe de crédit (booléen) |
| `taille_groupe` | Depuis `appartenance_groupe` |
| `taux_remboursement_groupe` | Part des crédits du groupe soldés sans incident, hors sociétaire évalué |
| `deja_secouru_par_groupe` | Le membre a-t-il déjà bénéficié d'un paiement par garant |

**Volontairement absentes :** degré de garant/bénéficiaire, taux de défaut du voisinage,
centralité, propagation de réputation — ces métriques de graphe supposent une densité de réseau
que ce portefeuille ne présente pas (ADR-016).

---

## 9. Proportions et calibrage

Les valeurs ci-dessous serviront de paramètres au générateur. Elles s'appuient sur des données publiques du secteur, mais **elles sont à confronter à la réalité d'une institution précise**.

### 9.1 Cibles issues de données publiques du secteur

| Paramètre | Valeur retenue | Origine |
|---|---|---|
| Taux de défaut global du portefeuille | **7 %** | Taux brut de dégradation du portefeuille des IMF togolaises : 4,2 % en 2022, 7,8 % en 2024, 6,7 % en 2025. Norme BCEAO : 3 % |
| Encours moyen de crédit par client | **~140 000 FCFA** | Ordre de grandeur régional UEMOA relevé par la BCEAO |
| Taux annuel appliqué | **18 à 24 %** | Plafond du taux d'usure pour les SFD : 24 % TAEG depuis le 1er juin 2026 |

### 9.2 Distributions proposées

**Part de membres emprunteurs** — ~25 % des sociétaires empruntent, les autres épargnent sans
emprunter. Calibré sur le bilan social FUCEC-TOGO (70 646 emprunteurs pour 287 643 sociétaires,
soit 24,6 %). C'est une donnée structurante : elle signifie que l'épargne, disponible pour 100 % des
membres, est le seul signal universel — d'où sa place centrale dans le modèle.

**Segments** (part des crédits) — salarié ~20 % (revenus domiciliés, très faible risque),
individuel ~32 % (petits métiers, commerce), jeune ~12 % (primo, thin-file), femme_gie ~18 %
(groupement, caution solidaire), agricole ~18 % (exposé au choc sectoriel). Calqué sur les
populations que la CIF cible explicitement (femmes, jeunes, petits exploitants agricoles,
entrepreneurs, commerçants, salariés).

**Montants de crédit** — loi log-normale, médiane 100 000 FCFA, plafond 3 000 000.

**Zone** — urbain 34 %, semi-urbain 30 %, rural 36 %.

**Type de garantie** — épargne nantie ~87 % (majoritaire, crédit individuel), caution solidaire de
groupe ~13 % (segment femme_gie uniquement). Ce déséquilibre n'est pas un défaut de calibrage : il
reflète le modèle mutualiste réel, où l'épargne nantie est la garantie de droit commun.

**Taille des groupes (GIE)** — distribution asymétrique entre 4 et 15, mode autour de 8.

**Numéro de cycle** — 45 % de primo-emprunteurs (cycle 1), 25 % cycle 2, 15 % cycle 3, 15 % cycle 4 et plus. Cette proportion est déterminante : elle détermine la part de dossiers en situation de démarrage à froid, que notre architecture en cascade doit traiter.

**Taux de défaut différencié** (structure à injecter dans la génération pour que le signal soit
apprenable — mécanismes calibrés sur la littérature du défaut en microfinance, pas sur une AUC
cible ; voir `03-MODELE/07-notebook-construction.md`) :

| Segment | Effet sur le risque |
|---|---|
| Salarié (revenus domiciliés) | Fortement protecteur |
| Régularité d'épargne élevée (≥ 9 mois sur 12) | Fortement protecteur |
| Agricole, exposition au choc sectoriel | Risque accru et variable dans le temps |
| Jeune, primo-accédant | Risque modérément accru |
| Cycle ≥ 3, sans incident antérieur | Protecteur |
| Groupe (segment femme_gie) au remboursement irréprochable | Protecteur, effet de sort partagé |
| Ratio d'endettement > 0,7 | Risque accru |

**Décision sur les demandes** — 78 % accordées, 7 % accordées partiellement, 12 % refusées, 3 % abandonnées.

**Délai d'instruction** — médiane 6 jours, 9e décile 21 jours, avec une variance délibérément différente entre agents pour matérialiser l'hétérogénéité.

**Taux de valeurs manquantes** — nous injecterons volontairement des manquants réalistes : revenu déclaré absent dans 15 % des cas, charges dans 25 %, niveau d'instruction dans 30 %. Un modèle qui ne fonctionne que sur des données parfaites n'est pas déployable.

> **[À VALIDER]** — Toutes les valeurs de cette section sont des hypothèses. Celles qui comptent le plus : la part de primo-emprunteurs, la répartition des types de garantie, et les taux de valeurs manquantes.

---

## 10. Ce que nous avons volontairement écarté

| Élément | Raison |
|---|---|
| Données mobile money (Flooz, Mixx by Yas) | Nécessite un accord de partage avec l'opérateur, hors de portée à court terme |
| Comptabilité générale, plan comptable SFD | Sans rapport avec le scoring d'octroi |
| Données de centrale des risques | Nous ignorons si les SFD togolais y ont accès en pratique — **à valider** |
| Géolocalisation fine des sociétaires | Sensibilité et faible disponibilité |
| Suivi IFRS 9 et provisionnement | Relève du suivi de portefeuille, pas de l'octroi |
| Mesures de centralité de graphe (betweenness, PageRank) | La densité de réseau qu'elles supposent n'existe pas dans un portefeuille de crédit individuel dominant (ADR-016) |
| Note qualitative de l'agent comme variable active | Prédictive en théorie, rarement structurée en pratique ; désactivée par défaut (ADR-017) |

> **[À VALIDER]** — Existe-t-il au Togo une centrale des risques ou un dispositif de partage d'information entre SFD auquel votre institution a accès ? Si oui, quels champs en proviennent ?

---

## 11. Synthèse des questions au valideur

1. Ces 13 tables correspondent-elles à la structure de votre système de gestion (SAB-AT ou autre) ?
2. Quels champs listés n'existent pas chez vous ?
3. Quels champs existent chez vous et manquent ici ?
4. **Quelle est la part réelle du portefeuille en crédit de groupe / caution solidaire**, par
   rapport au crédit individuel adossé à l'épargne ? C'est la question qui calibre toute la couche
   solidaire (section 5) — la réponse peut confirmer ou déplacer le curseur ~13-18 % retenu par défaut.
5. Existe-t-il une **note ou appréciation qualitative de l'agent** après visite terrain, et sous
   quel format ? Nous la laissons désactivée par défaut (ADR-017) faute de certitude sur son format.
6. Les **demandes refusées** sont-elles conservées ?
7. Les **cautions individuelles hors groupe** sont-elles enregistrées de manière structurée ?
8. Le système trace-t-il qu'une **garantie a été appelée** ou qu'un remboursement a été **payé par le garant** ?
9. Quel **seuil de retard** définit la créance en souffrance chez vous ?
10. Quelle est la part réelle de **primo-emprunteurs** dans vos dossiers ?
11. Quels champs sont, en pratique, **souvent vides** ?

---

*Document préparatoire, version 1.0. Toutes les données décrites sont destinées à être générées synthétiquement. Aucune donnée réelle de sociétaire n'est ni collectée ni utilisée.*
