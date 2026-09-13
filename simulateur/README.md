# SOLIDA -- Generateur CORE-SIM v4

Le generateur produit les donnees brutes d'une cooperative d'epargne et de credit.
Il est reproductible avec une graine unique et conserve une separation stricte entre
les informations connues a l'octroi et les issues observees apres decaissement.

## Decisions terrain J1-05 a J1-13

- Tous les produits exigent trois mois d'epargne avant le premier credit.
- Le catalogue n'impose aucun minimum metier et porte un plafond institutionnel de
  100 000 000 FCFA. Les montants synthetiques suivent une loi log-uniforme entre
  20 000 et 5 500 000 FCFA, sans progression automatique entre les cycles.
- La faisabilite d'un credit individuel depend de l'epargne libre disponible pour
  nantir entre 10 % et un tiers du montant. Si aucune combinaison n'est possible,
  le credit n'est pas genere.
- Le seuil d'endettement est configurable a 33 %. La pente du risque est conservee
  sous le seuil et double sur la portion qui le depasse. L'endettement vaut exactement
  `charge_mensualisee / revenu_declare`.
- Les periodicites hebdomadaire, mensuelle, trimestrielle, semestrielle et annuelle
  ont chacune un poids initial de 20 %. Elles sont filtrees selon la duree : trimestre,
  semestre et annee exigent respectivement un multiple de 3, 6 et 12 mois.
- Les echeances sont constantes. A chaque periode, les interets sont calcules sur le
  capital restant du ; leur part diminue donc au fil du remboursement.
- Une alerte operationnelle apparait des J+1. Le defaut commence a 30 jours de retard.
- Les paiements, retards, statuts et defauts sont des issues post-decaissement. Ils ne
  participent jamais au mecanisme de risque a l'octroi, pas plus que l'age, les visites
  ou les relances. Toutes les anciennetes sont calculees a la date du credit.
- `age` reste renseigne pour chaque societaire. Aucune `date_naissance` n'est ajoutee
  et aucun refus automatique n'est applique apres 73 ans.
- L'historique d'epargne commence a l'ouverture du compte : 15 % des societaires ont
  3 a 5 mois, 25 % en ont 6 a 11 et 60 % au moins 12, jusqu'a 14 ans.
- Le solde initial est nul. Les depots, retraits, transferts et restitutions de nantie
  sont journalises. Le type `interet` est reserve, mais aucun interet d'epargne n'est
  genere tant que son taux et sa frequence ne sont pas confirmes.
- La nantie est retiree de l'epargne libre au deblocage. Elle est restituee si le credit
  est solde et reste bloquee si le credit est en cours ou en souffrance. Elle demeure
  dans `garanties`, sans creer de second compte.
- Un remboursement de credit GIE est enregistre au niveau `groupe`, jamais sur chacun
  des membres.

Les frais, assurances, annulations, regularisations et interets d'epargne restent hors
generation faute de regles chiffrees confirmees. La part des credits de groupe, les
demandes refusees, les objets de credit et la saisonnalite ne sont pas modifies ici.

## Produits et taux annuels

| Segment | Produit | Taux |
|---|---|---:|
| `jeune` | Youth Espoir | 7 a 7,5 % |
| `individuel` | Credit PME/PMI | 14 % |
| `salarie` | Virement salaire | 9 a 12 % |
| `femme_gie` | Credit Epargne avec Education (CEE) | 16 % |
| `agricole` | Credit agricole | 14 % |

Un taux variable est tire uniformement dans sa fourchette et stocke sur le credit.
Le catalogue expose `taux_annuel_min`, `taux_annuel_max` et conserve `taux_annuel`
a la moyenne de la fourchette pour les lecteurs existants.

## Sorties

- `societaires.parquet`
- `credits.parquet`
- `echeances.parquet`
- `produits_credit.parquet`
- `comptes_epargne.parquet`
- `mouvements_epargne.parquet`
- `solde_mensuel_epargne.parquet`
- `groupes_gie.parquet`, `appartenances_gie.parquet`, `garanties.parquet`
- `choc_secteur.parquet`

`solde_mensuel_epargne.parquet` est reconstruit par accumulation chronologique. Le
dernier solde mensuel correspond a `comptes_epargne.solde_actuel`; les anciens agregats
6/12 mois restent presents et sont derives de cette trajectoire pour compatibilite.
Les dates de paiement reelles et les mouvements ne depassent jamais `date_fin`. Les
dates d'echeance futures d'un credit en cours restent naturellement dans le calendrier
contractuel. Pour l'entrainement, un credit n'est etiquete comme resolu que si sa maturite
et la fenetre d'observation de 30 jours sont toutes deux anterieures a `date_fin`.

## Utilisation et validation

```bash
python simulateur/simulateur/pipeline.py
python -m unittest discover -s simulateur/tests -v
python simulateur/simulateur/demo_recherche.py "MENSAH"
```

Le fichier `config/config.yaml` fixe par defaut 27 000 societaires afin d'obtenir environ
10 000 credits resolus pour l'entrainement. Pour l'entrainement,
l'unite statistique est le credit resolu (`defaut` egal a 0 ou 1), pas le societaire ni
chaque mouvement. La taille exacte du dataset d'entrainement est donc publiee par le
rapport de generation et non imposee artificiellement.

La formule d'annuite suit la definition de PMT : taux et nombre de periodes utilisent
la meme unite, sans frais ni assurance. Les offsets calendaires pandas construisent les
dates mensuelles, trimestrielles, semestrielles et annuelles.

## Frontiere avec le modele

Le feature engineering, l'entrainement et le moteur de decision ne sont pas implementes
dans ce dossier. Leur specification vit dans `03-MODELE/`. Le generateur ne cible aucune
AUC : il calibre seulement la marginale globale des credits resolus autour de 9 % de
defaut, puis expose les donnees brutes necessaires a un modele explicable et temporellement
valide.
