# Spécification des écrans

Chaque écran est décrit par : objectif, structure, contenu, données consommées, états, interactions.
**Aucun code.** Ce document est la source de vérité pour l'implémentation.

Priorités selon `00-CONTEXTE/03-perimetre-hackathon.md`.

---

## E0 — Connexion — P0

**Objectif :** authentifier l'agent et établir la session.

**Structure :** page pleine hauteur, deux zones.
- Gauche (55 %) : fond `--solida-teal-900`, logo SOLIDA centré, sous-titre
  « Scoring d'octroi pour coopératives financières », mention discrète du programme
  DigiCoop-WA+ en bas. C'est le seul endroit de l'application où `AnimatedBeam` peut évoquer
  le flux d'épargne, en très basse opacité.
- Droite (45 %) : fond blanc, formulaire centré, largeur 360 px.

**Formulaire :** identifiant, mot de passe, bouton « Se connecter » pleine largeur en
`--solida-teal-800`. Aucun lien « créer un compte » — les agents sont créés par l'administrateur.

**États :** repos, en cours (bouton désactivé, libellé « Connexion… »), erreur (message sous le
formulaire, jamais en notification flottante : « Identifiant ou mot de passe incorrect. »).

**Interactions :** Entrée valide. Focus initial sur l'identifiant.

---

## E1 — Recherche de sociétaire — P0 — **écran central du produit**

**Objectif :** permettre à l'agent de retrouver un sociétaire en tapant un nom, puis d'ouvrir son
dossier.

**Structure :** écran volontairement vide, centré verticalement au tiers supérieur.

```
┌──────────────────────────────────────────────────────────────┐
│  [en-tête 56px : logo · agence · utilisateur]                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│              Rechercher un sociétaire                        │
│              (titre, texte-xl)                               │
│                                                              │
│    ┌────────────────────────────────────────────────┐        │
│    │ 🔍  Nom, numéro de membre ou numéro de compte  │        │
│    └────────────────────────────────────────────────┘        │
│      largeur 560px, hauteur 44px (exception assumée :        │
│      c'est l'action principale de l'écran)                   │
│                                                              │
│    ┌────────────────────────────────────────────────┐        │
│    │ liste de suggestions — élévation 1             │        │
│    └────────────────────────────────────────────────┘        │
│                                                              │
│    Dossiers récents                                          │
│    [3 à 5 puces cliquables, texte-sm, neutre-700]            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Champ de recherche :** composant `Command` de shadcn. Hauteur 44 px (seule exception à la règle
des 36 px, justifiée par son statut d'action principale). Icône `Search` à gauche. Focus
automatique au chargement de la page.

**Liste de suggestions — structure d'une ligne :**

```
┌─────────────────────────────────────────────────────────────┐
│  ADJO Kokou Mensah                    ● Crédit en cours     │
│  N° 004512 · Agence Bè · Semi-urbain                        │
└─────────────────────────────────────────────────────────────┘
```

- Ligne 1 : nom en `texte-sm` graisse 500, `--neutre-950`. À droite, pastille d'état.
- Ligne 2 : numéro de membre, agence, zone, en `texte-xs`, `--neutre-500`, séparés par `·`.
- Hauteur de ligne : 52 px. Maximum 8 résultats visibles, défilement au-delà.
- La portion du nom correspondant à la saisie est en graisse 600, **jamais surlignée en couleur**.
- Ligne survolée ou sélectionnée au clavier : fond `--solida-teal-50`, barre gauche 2 px en
  `--solida-teal-800`.

**Comportement :**
- Déclenchement à partir de 2 caractères, requête différée de 250 ms.
- Insensible aux accents et à la casse, tolérante à l'approximation.
- Navigation `↑` `↓`, validation `Entrée`, fermeture `Échap`.

**États :**
- Chargement : trois lignes squelette dans le panneau.
- Aucun résultat : « Aucun sociétaire ne correspond à *terme*. Vérifiez l'orthographe ou essayez
  le numéro de membre. »
- Trop de résultats : afficher les 8 premiers + « 34 autres résultats — précisez votre recherche ».
- Erreur : « La recherche est momentanément indisponible. » + bouton « Réessayer ».

**Interdits sur cet écran :** aucun tableau de bord, aucun indicateur, aucune statistique. L'écran
sert à une seule chose.

---

## E2 — Dossier du sociétaire (vue 360°) — P0

**Objectif :** donner à l'agent, en un écran sans défilement sur un écran standard, tout ce que le
système sait déjà du sociétaire.

**Structure :** en-tête d'identité, puis grille de 12 colonnes.

### Bandeau d'identité (pleine largeur, hauteur 88 px)

```
┌───────────────────────────────────────────────────────────────────────┐
│ [avatar]  ADJO Kokou Mensah              [Salarié]  [Nouvelle demande]►│
│           N° 004512 · Sociétaire depuis mars 2019 (5 ans 4 mois)      │
│           Agence Bè · Commerce · Semi-urbain                          │
│           ● Actif    ● 1 crédit en cours    ● Épargne nantie          │
└───────────────────────────────────────────────────────────────────────┘
```

Le badge de segment (`Salarié`, `Individuel`, `Jeune`, `Groupement`, `Agricole`) est visible en
permanence : il conditionne quelle carte apparaît en colonne droite (garantie individuelle ou
groupe). Le bouton « Nouvelle demande » est le seul bouton plein de l'écran, en `--solida-teal-800`.

### Colonne gauche (5 colonnes) — profil et activité

Deux cartes empilées, élévation 0.

**Carte « Profil »** : âge, personnes à charge, statut du logement, niveau d'instruction,
parts sociales. Présentation en paires libellé / valeur, libellé `texte-xs` `--neutre-500`,
valeur `texte-sm` `--neutre-950`, deux colonnes internes.

**Carte « Activité économique »** : secteur, ancienneté de l'activité, revenu mensuel déclaré,
charges déclarées, **capacité de remboursement estimée** (mise en valeur, IBM Plex Mono).
Si le revenu est absent : « Non renseigné » en `--neutre-500` italique, avec une icône
`AlertTriangle` en `--alerte` et une infobulle « Ce champ est absent du dossier et sera imputé
lors du scoring, ce qui réduit la précision. »

### Colonne centrale (4 colonnes) — épargne

**Carte « Trajectoire d'épargne »**, la plus visuelle de l'écran — c'est le signal central du
score, pas un simple solde.

- Chiffre principal : solde moyen sur 6 mois, `texte-lg`, IBM Plex Mono, avec une flèche de
  tendance (`↗ en hausse` / `→ stable` / `↘ en érosion`) sur les 12 derniers mois.
- Courbe Recharts de l'évolution du solde sur 12 mois. Hauteur 120 px, une seule série, trait
  `--solida-teal-700` de 1,5 px, aire remplie à 8 % d'opacité, pas de point sauf au survol.
- En dessous : bande de 12 petits carrés de 14 px représentant les mois. Carré plein
  `--solida-teal-600` si dépôt, carré vide bordé `--neutre-300` sinon. Légende :
  « Dépôts effectués : 11 mois sur 12 ». Cette bande est plus lisible qu'un graphique et se
  comprend instantanément, y compris par le sociétaire.
- Ligne discrète : « Sociétaire depuis 64 mois — relation d'épargne antérieure à toute demande de
  crédit. » Elle rappelle que ce signal existe même pour un primo-emprunteur.

### Colonne droite (3 colonnes) — garantie

**Cas majoritaire (segment salarié / individuel / jeune / agricole) — carte « Épargne nantie »** :
montant nanti, ratio par rapport au montant du dernier crédit, avec une pastille de couleur
sémantique. C'est la garantie de droit commun dans le modèle mutualiste.

**Cas du segment groupement (`femme_gie`) — carte « Groupe de caution »** : nom du groupe, taille,
date de création, taux de remboursement du groupe affiché en grand avec une pastille de couleur
sémantique. Lien « Voir le groupe » ouvrant E5.

Si le sociétaire du segment groupement n'a pas encore d'historique de groupe suffisant : état vide
explicite — « Le groupe ne dispose pas encore d'un historique de remboursement suffisant. Le
scoring s'appuiera sur le profil individuel. » Cet état est **normal**, il ne doit pas ressembler à
une erreur.

### Bande inférieure (12 colonnes) — historique de crédit

Tableau dense, lignes de 40 px, colonnes : date de déblocage, montant octroyé, durée, cycle,
statut (badge), capital restant dû, retard maximal observé.

- Montants alignés à droite, chiffres tabulaires.
- Statut en badge : couleurs sémantiques de décision.
- Retard maximal : neutre si 0, `--alerte` si 1-30, `--decision-refus` au-delà de 90.
- Si aucun crédit : « Premier crédit — ce sociétaire n'a pas d'historique d'emprunt. »
  Cet état est fréquent et doit être présenté sans dramatisation.

**Fraîcheur des données :** en bas d'écran, mention discrète `texte-xs` `--neutre-500` :
« Données consolidées le 2 septembre 2026 à 03h12. » Elle est importante : elle rend visible
l'architecture batch et rassure sur l'origine des chiffres.

---

## E3 — Nouvelle demande de crédit — P0

**Objectif :** saisir la demande du jour. **Quatre champs, pas davantage.**

**Structure :** panneau latéral droit de 460 px glissant depuis la droite (composant `Sheet`),
avec le dossier resté visible à gauche. Ce choix évite de perdre le contexte du sociétaire.

**Contenu du panneau :**

```
Nouvelle demande — ADJO Kokou Mensah
─────────────────────────────────────

Produit de crédit
[Select : Crédit commerce · Crédit agricole · ...]

Montant sollicité
[Input numérique]  FCFA
Plafond du produit : 2 000 000 FCFA

Durée
[Select : 3, 6, 9, 12, 18, 24 mois]

Objet du crédit
[Select : Fonds de roulement · Équipement · Intrants agricoles · ...]

─────────────────────────────────────
▸ Actualiser la situation économique   (repliable, fermé par défaut)
    Revenu mensuel        [pré-rempli, modifiable]
    Charges mensuelles    [pré-rempli, modifiable]
    Personnes à charge    [pré-rempli, modifiable]

─────────────────────────────────────
Échéance mensuelle estimée : 108 500 FCFA
Taux d'endettement résultant : 0,42

        [Annuler]        [Calculer le score]
```

**Points de conception :**

- Le bloc « Actualiser la situation » est **replié par défaut**. Les valeurs viennent du dossier ;
  l'agent ne les ressaisit que si elles ont changé. C'est la traduction concrète du principe de
  saisie minimale.
- L'échéance estimée et le taux d'endettement se recalculent en direct à chaque frappe. Ce sont
  des calculs déterministes côté client, ils n'appellent pas le serveur.
- Le taux d'endettement change de couleur au-delà de 0,7 (`--alerte`) — sans bloquer.
- Aucune variable de la couche solidaire, aucune variable d'épargne, aucun historique n'est saisissable ici.
  **Si un tel champ apparaît, c'est une régression.**

**Validation :** montant dans les bornes du produit, durée dans les bornes, tous les champs
obligatoires renseignés. Message d'erreur sous le champ concerné, en français.

---

## E4 — Résultat du scoring — P0 — **écran de la démonstration**

**Objectif :** restituer le score, la recommandation et sa justification.

C'est l'écran que le jury regardera. Il doit être sobre, dense et immédiatement lisible.

**Structure :** deux colonnes, 5 / 7.

### Colonne gauche (5) — le verdict

**Bloc de décision**, carte élévation 0, bordure gauche de 3 px en couleur sémantique de la
tranche, fond en teinte claire associée.

```
┌───────────────────────────────────────────┐
│▌                                          │
│▌   Recommandation                         │
│▌                                          │
│▌            586                           │  ← texte-score, IBM Plex Mono
│▌      points sur 850                      │
│▌                                          │
│▌   ACCORD SOUS CONDITION                  │  ← texte-lg, graisse 600
│▌                                          │
│▌   Montant recommandé                     │
│▌   875 000 FCFA                           │  ← IBM Plex Mono, texte-lg
│▌   sur 1 250 000 FCFA sollicités          │
│▌                                          │
│▌   La décision finale relève de l'agent   │
│▌   et du comité de crédit.                │  ← texte-xs, neutre-500
└───────────────────────────────────────────┘
```

- Le score s'incrémente de 0 à sa valeur en 600 ms (`NumberTicker`), une seule fois, sans rebond.
- Sous le score, une **barre de position** horizontale de 6 px montrant les quatre tranches et un
  repère à la position du score. Pas de jauge circulaire, pas d'aiguille.
- Le libellé de la tranche est écrit en toutes lettres. La couleur ne porte jamais seule
  l'information.

**Bandeau de mode de calcul**, juste sous le bloc, `texte-xs` :
- Mode enrichi : icône `Users` + « Score calculé avec l'historique du groupe de caution
  (segment groupement). »
- Mode socle : icône `User` + « Score calculé sur le profil individuel et l'épargne : la
  garantie de ce crédit est l'épargne nantie. » Formulation neutre, **jamais** « données
  manquantes » — c'est le cas de la majorité du portefeuille, pas une exception.

**Avertissements** éventuels, en `Alert` sobre : « Le revenu déclaré était absent du dossier ; une
valeur médiane du secteur a été utilisée. »

**Bloc « Trajectoire de progression »** (affiché quel que soit le mode) : sous le bloc de décision,
carte compacte listant, pour les 3 prochains cycles, le plafond accessible si le sociétaire
rembourse sans incident — issu du moteur de crédit progressif (`plafond × coefficient_progression`,
plafonné au produit). Rend visible que le système ne s'arrête pas à un chiffre, il ouvre une
trajectoire.

**Bloc « Conditions de réexamen »**, affiché seulement si la décision n'est pas ACCORD simple :
liste à puces des leviers concrets et vérifiables (« porter la régularité d'épargne à 9 mois sur
12 », « porter l'épargne nantie à 50 % du montant sollicité »). C'est ce qui transforme un refus en
parcours d'éligibilité plutôt qu'en porte fermée — voir `03-MODELE/03-scorecard-et-grille.md`.

### Colonne droite (7) — la justification

**Titre :** « Facteurs déterminants »

**Graphique de contributions** : barres horizontales divergentes, axe zéro central.

```
Régularité de l'épargne         11/12 mois      ████████ +31
Ancienneté de sociétariat       5 ans 4 mois    ██████ +24
Réputation du groupe            97 % remb.      ███ +12
Cycle de crédit                 3e crédit       ██ +9
─────────────────────────────── 0 ──────────────────────
Taux d'endettement              0,58            ██████ −18
Montant / historique            × 1,8           ████ −14
```

- Barres favorables : `--decision-accord`. Défavorables : `--decision-refus`. Opacité 0,85.
- Hauteur de barre 20 px, espacement 10 px.
- Libellé métier à gauche, valeur réelle au centre, points à droite en IBM Plex Mono.
- Tri par valeur absolue décroissante, 8 lignes maximum, puis « + 5 autres facteurs » repliable.
- Apparition décalée de 25 ms par ligne, 200 ms de durée, une seule fois.

**Sous le graphique :** ligne de vérification, `texte-xs`, `--neutre-500` :
« Base 487 + contributions 99 = 586 ». Cette ligne paraît anodine ; elle démontre visuellement que
la décomposition est **exacte** et non approchée. C'est un argument technique fort, à laisser visible.

**Actions en bas d'écran :** `[Générer la fiche de justification]` (bouton plein),
`[Enregistrer la décision]`, `[Nouvelle recherche]` (tertiaire).

**Interdits sur cet écran :** aucune probabilité en pourcentage, aucun terme de machine learning,
aucun logo de librairie, aucune animation autre que celles listées.

---

## E5 — Groupe de caution (segment groupement) — P1

**Objectif :** montrer la composition et l'historique du groupe de caution du sociétaire. Réservé
au segment groupement (`femme_gie`) — l'écran n'existe pas pour les autres segments, dont la
garantie est l'épargne nantie et n'a pas d'équivalent collectif à afficher.

**Structure :** modale (720 × 560) ou panneau dédié. **Une liste, pas une visualisation de
réseau** (voir `01-ARCHITECTURE/07`, ADR-016) : la structure réelle d'un groupe de 4 à 15 membres
se lit plus vite dans un tableau trié que dans un diagramme de nœuds, et n'introduit pas de fausse
impression de complexité relationnelle là où il n'y en a pas.

**En-tête :** nom du groupe, date de création, taille, taux de remboursement collectif affiché en
grand.

**Corps :** tableau des membres — nom, ancienneté dans le groupe, rôle (membre / présidente /
trésorière), statut de leurs crédits (badge), une colonne « caution appelée » si applicable. Le
sociétaire consulté est mis en évidence (fond `--solida-teal-50`).

**Bas d'écran :** synthèse chiffrée — nombre de cycles menés à terme par le groupe, nombre de
sorties sur 12 mois (signal de fragilité). Aucune animation, aucune disposition calculée : c'est un
tableau, il s'exporte et se lit comme tel.

**Interaction :** clic sur une ligne → ouvre le dossier de ce sociétaire (E2).

---

## E6 — Fiche de justification — P1

**Objectif :** produire le document remis au sociétaire.

**Structure :** aperçu au format A4 (ratio respecté) dans un panneau, action d'export à droite.

**Contenu de la fiche :** voir `07-export-pdf.md`. Si la décision n'est pas un accord simple, la
fiche inclut la section « Conditions de réexamen » (mêmes leviers que sur E4) — c'est un document
que le sociétaire peut relire et agir dessus, pas seulement une trace de refus.

**Actions :** « Télécharger le PDF », « Imprimer », « Archiver au dossier ».

**État de génération :** progression nommée — « Génération de la fiche… » — et non un spinner.

---

## E7 — Registre des décisions — P2

**Objectif :** traçabilité et audit.

**Structure :** filtres en haut (période, agence, agent, tranche), tableau dense en dessous.

**Colonnes :** date et heure, sociétaire, agent, montant sollicité, score, tranche, décision
finale prise, écart avec la recommandation.

La colonne **écart** est la plus intéressante : elle montre quand un agent a décidé autrement que
la recommandation. C'est un indicateur de pilotage réel, et un excellent point de démonstration.

**Ligne cliquable** → rejeu complet de la décision, avec la version du modèle et de la grille
utilisées à l'époque.

---

## E8 — Paramétrage de la grille — P2

**Objectif :** permettre au superviseur d'ajuster les seuils sans réentraîner le modèle.

**Structure :** quatre curseurs pour les bornes de tranche, un champ PDO, un champ score de
référence.

**Élément clé :** un aperçu en direct qui affiche, sur l'historique, la répartition des dossiers
dans chaque tranche selon les seuils choisis, et le taux de défaut historique associé. Le
superviseur voit immédiatement l'effet de son arbitrage sur le taux d'approbation.

Toute modification est journalisée et versionnée (`version_grille`).

---

## E9 — Supervision du modèle — Abandonné

**Décision produit :** pas d'écran maison pour la supervision du modèle ou la dérive. Des outils
spécialisés déjà éprouvés (MLflow, Prometheus/Grafana, Evidently) couvrent ce besoin sans
réimplémentation partielle côté SOLIDA — voir `07-MLOPS/06-outils.md`. Aucune route frontend n'est
prévue pour cet écran.

---

## Tableau récapitulatif

| Écran | Priorité | Route | Rôles |
|---|---|---|---|
| E0 Connexion | P0 | `/connexion` | public |
| E1 Recherche | P0 | `/` | agent, superviseur |
| E2 Dossier | P0 | `/societaires/[id]` | agent, superviseur |
| E3 Nouvelle demande | P0 | panneau sur E2 | agent |
| E4 Résultat | P0 | `/scoring/[id]` | agent, superviseur |
| E5 Groupe de caution | P1 | modale sur E2 | agent, superviseur |
| E6 Fiche | P1 | `/scoring/[id]/fiche` | agent, superviseur |
| E7 Registre | P2 | `/registre` | superviseur, auditeur |
| E8 Grille | P2 | `/parametrage/grille` | superviseur |
| E9 Modèle | Abandonné | — | — (outils spécialisés, voir `07-MLOPS/06-outils.md`) |
