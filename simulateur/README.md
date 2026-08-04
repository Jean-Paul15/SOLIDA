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
GIE et appartenances, garanties (epargne nantie OU caution solidaire GIE). Rien
de pre-calcule. Il encode la structure reelle, dont la contagion GIE (documentee).

**Feature engineering (`features.py`)** = derive les variables du modele, en trois
blocs, toutes leak-free (a la date de deblocage) :
- **SOCLE (universel)** : regularite et anciennete d'epargne, ratio epargne
  nantie/credit, historique de remboursement (jours de retard, incidents),
  endettement, cycle, anciennete, segment.
- **SOLIDAIRE (conditionnel, GIE)** : remboursement du groupe, taille, deja secouru.
- **SECTORIEL** : degradation recente du secteur.

## Reproductible, dates bornees

Une seule graine gouverne tout. Aucun evenement ne depasse `date_fin` (2026-08-01) :
le controle `evenements_apres_date_fin` vaut 0. Les credits encore en cours a cette
date ne sont pas etiquetes (exclus de la modelisation).

## Utilisation

```bash
python3 simulateur/pipeline.py        # genere sorties/*.parquet + rapport coherence
python3 simulateur/features.py        # construit la matrice de variables (verif couverture)
python3 simulateur/valider.py         # performance emergente + matrice d'argent + interpretation
python3 simulateur/decision.py        # grille parametrable, plafond progressif, fiche actionnable
python3 simulateur/demo_recherche.py "MENSAH"   # dossier 360 d'un membre (demo agent)
DATABASE_URL=postgresql://... python3 simulateur/charger_postgres.py
```

Passer a l'echelle : `n_membres: 25000` dans `config/config.yaml`.

## Resultat mesure (graine 42)

Structure : 25,0% de membres emprunteurs, defaut en souffrance ~8,9%, GIE ~18%
des credits, salaries ~22%, garanties = epargne nantie dominante + caution GIE
en minorite. Performance emergente : socle AUC ~0,69 (regularite d'epargne,
segment salarie, ratio de garantie et conditions sectorielles en tete des
variables). Matrice d'argent : ~17% des pertes evitees au seuil economique ;
les 20% de dossiers les plus risques concentrent ~40% des souffrances. La couche
solidaire apporte un gain reel mais modeste sur le seul segment GIE, sous-estime
par le demarrage a froid synthetique (plus fort sur portefeuille reel mature).

## Moteur de décision (`decision.py`)

Au-dessus du score : une grille de décision paramétrable (dérivée de la matrice de coûts, pas
arbitraire), un plafond de crédit progressif avec trajectoire sur 3 cycles, et des **conditions de
réexamen actionnables** quand la décision n'est pas un accord simple. Rien n'est une boîte noire :
chaque règle est lisible dans `decision.py` et modifiable par caisse.

## Honnetete pour le jury

Donnees synthetiques calibrees sur la litterature et sur les chiffres reels des
reseaux CIF (sans donnees reelles, les modeles appris type GAN sont hors de portee).
Le coeur du score est l'epargne et le comportement de remboursement -- ce qui existe
dans CHAQUE SIG COOPEC. Le solidaire n'est active que la ou la donnee de groupe existe.
