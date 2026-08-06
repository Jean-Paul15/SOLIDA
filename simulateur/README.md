# SOLIDA -- Generateur CORE-SIM v3 (logique COOPEC / CIF)

Donnees synthetiques pour un systeme de scoring de microcredit, cale sur la
realite des reseaux mutualistes de la CIF (FUCEC, RCPB, PAMECAS, FECECAM,
Kafo Jiginew, Nyesigiso). Hackathon CIF / DigiCoop-WA+ 2026, Thematique 02.

## Le principe : suivre la logique COOPEC

Les reseaux CIF sont d'abord des **caisses d'epargne** : on epargne, puis on
emprunte. Le generateur reproduit ce modele reel :

- **tout le monde epargne** ; l'epargne est la porte d'entree du credit et le
  signal central du score ;
- **~25% des membres empruntent** (bilan social FUCEC : 70 646 emprunteurs pour
  287 643 societaires) ;
- **credit individuel dominant, adosse a l'epargne (epargne nantie)** ; la
  **caution solidaire est un SEGMENT** (GIE femmes), pas le coeur ;
- **defaut = creance en souffrance (PAR 90j)**, calibre ~9% (secteur Togo ~11%,
  norme prudentielle 3%).

La performance du modele **emerge** des donnees ; on ne cible jamais une AUC.

## Deux couches strictement separees

**Generateur (`pipeline.py`)** = uniquement les tables BRUTES du SIG : membres,
comptes et mouvements d'epargne, credits (echeancier, jours de retard, statut),
GIE et appartenances, garanties (epargne nantie OU caution solidaire GIE),
produits de credit (referentiel). Rien de pre-calcule. Il encode la structure
reelle, dont la contagion GIE (documentee).

**Referentiel `produits_credit`** : un produit par segment (correspondance 1:1,
confirmee par la typologie publique de FUCEC-Togo/RCPB/PAMECAS -- credit sur
salaire domicilie, individuel, YouthStart jeunes, Credit Epargne avec Education
pour les GIE femmes, agricole). Aucune de ces institutions ne publie de plafond/
duree/taux precis par produit (donnee interne non publique) : les valeurs de
`config/config.yaml` sont un point de depart calibre et ajustable, pas une
verite mesuree -- meme statut que les autres parametres de ce fichier. Chaque
credit genere porte le `produit_id` de son segment ; `montant_octroye` et
`duree_mois` sont bornes par les valeurs du produit plutot que par un plafond
global unique.

**Feature engineering** : la specification (trois blocs SOCLE / SOLIDAIRE / SECTORIEL,
regle "leak-free a la date de deblocage") vit desormais dans
`03-MODELE/02-feature-engineering.md`, pas dans ce depot. Le prototype qui vivait ici
(`features.py`) a ete retire -- voir `03-MODELE/09-lecons-prototype-simulateur.md`.

## Reproductible, dates bornees

Une seule graine gouverne tout. Aucun evenement ne depasse `date_fin` (2026-08-01) :
le controle `evenements_apres_date_fin` vaut 0. Les credits encore en cours a cette
date ne sont pas etiquetes (exclus de la modelisation).

## Utilisation

```bash
python3 simulateur/pipeline.py        # genere sorties/*.parquet + rapport coherence
python3 simulateur/demo_recherche.py "MENSAH"   # dossier 360 d'un membre (demo agent)
DATABASE_URL=postgresql://... python3 simulateur/charger_postgres.py
```

Passer a l'echelle : `n_membres: 25000` dans `config/config.yaml`.

## Feature engineering, entrainement, decision : plus ici

Ce depot ne contient plus que le generateur de donnees brutes. Le prototype jetable qui
demontrait la faisabilite (feature engineering, entrainement d'un classifieur de
validation, moteur de decision) a ete retire : son role etait de prouver que les donnees
synthetiques produisent un signal plausible avant que le vrai modele et le vrai backend
n'existent, et il comportait des ecarts (fuite temporelle, coefficient non cable) qui le
rendaient trompeur s'il restait dans le depot sans etre maintenu. Le contenu correct est
deja specifie, en mieux, dans `03-MODELE/` (feature engineering, scorecard et grille,
evaluation et metriques) et implemente reellement dans `backend/solida/domain/rules/`
(`progressif.py`, `grille.py`, `scorecard.py`). Le detail de ce qui a ete retire et pourquoi
est dans `03-MODELE/09-lecons-prototype-simulateur.md`.

## Honnetete pour le jury

Donnees synthetiques calibrees sur la litterature et sur les chiffres reels des
reseaux CIF (sans donnees reelles, les modeles appris type GAN sont hors de portee).
Le coeur du score est l'epargne et le comportement de remboursement -- ce qui existe
dans CHAQUE SIG COOPEC. Le solidaire n'est active que la ou la donnee de groupe existe.
