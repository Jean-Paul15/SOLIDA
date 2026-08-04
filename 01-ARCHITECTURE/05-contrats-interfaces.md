# Contrats d'interface

**Ce fichier est le document le plus important pour le travail en parallèle.**

Un contrat gelé permet à chacun de coder son module contre une doublure, sans attendre les autres.
Celui qui fait le front code contre un `ScoringResult` factice ; celui qui fait le modèle produit
un `ScoringResult` conforme ; le jour du câblage, cela s'emboîte.

**Un contrat ne se modifie pas unilatéralement.** Toute évolution passe par une annonce à l'équipe
et une entrée dans le journal de décisions.

Les structures ci-dessous sont décrites en pseudo-spécification. Les types sont indicatifs
(`entier`, `texte`, `décimal`, `date`, `liste<T>`, `optionnel<T>`).

---

## 1. Identité et entrée du scoring

### `IdentifiantSocietaire`
```
societaire_id : texte          # opaque, jamais interprété par le front
```

### `EntreeScoring`
Ce que l'agent fournit réellement à l'écran. Volontairement minimal.
```
societaire_id        : texte
produit_id           : texte
montant_demande      : entier          # FCFA
duree_demandee_mois  : entier
objet_credit         : enum            # fonds_roulement | equipement | intrants_agricoles |
                                       # stock | urgence_sante | scolarite | habitat | autre
groupe_id            : optionnel<texte>
actualisation        : optionnel<ActualisationSituation>
```

### `ActualisationSituation`
Champs que l'agent peut corriger au guichet si la situation a changé.
```
revenu_mensuel_declare      : optionnel<entier>
charges_mensuelles          : optionnel<entier>
nb_personnes_a_charge       : optionnel<entier>
```

**Règle absolue :** aucune variable dérivée (épargne agrégée, historique, couche solidaire) n'apparaît
dans `EntreeScoring`. Ces données sont récupérées par le système à partir du `societaire_id`. Si un
jour une telle variable apparaît dans ce contrat, c'est que l'architecture a dérivé.

---

## 2. Instantané interne

### `InstantaneSocietaire`
Assemblé par le backend, jamais saisi.
```
societaire_id            : texte
nom_complet              : texte
date_adhesion            : date
age                      : entier
zone_residence           : enum
secteur_activite         : enum
anciennete_activite_mois : entier
agence_id                : texte
features_individuelles   : FeaturesIndividuelles
features_solidaires  : optionnel<FeaturesSolidaires>
fraicheur_features       : date            # date du dernier batch
```

### `FeaturesIndividuelles`
```
anciennete_societaire_mois   : entier
segment                      : enum       # salarie | individuel | jeune | femme_gie | agricole
solde_epargne_moyen_6m       : entier
nb_mois_avec_depot_12m       : entier      # 0 à 12
tendance_epargne_12m         : enum        # hausse | stable | erosion
volatilite_epargne           : décimal
ratio_epargne_revenu         : décimal     # effort d'épargne
ratio_epargne_montant        : décimal     # garantie : épargne / montant demandé
anciennete_epargne_mois      : entier      # depuis date_adhesion, disponible dès le 1er credit
ratio_endettement            : décimal
nb_credits_anterieurs        : entier
nb_incidents_anterieurs      : entier
max_jours_retard_historique  : entier
montant_max_rembourse        : entier
numero_cycle                 : entier
parts_sociales_montant       : entier
nb_personnes_a_charge        : entier
```

**La trajectoire d'épargne est le bloc le plus dense de ce contrat, à dessein : elle est le
signal central du modèle et le seul disponible pour 100 % du portefeuille (voir
`03-MODELE/02-feature-engineering.md`).**

### `FeaturesSolidaires`
```
en_groupe                    : booléen     # faux pour la majorité du portefeuille
groupe_id                    : texte, nullable
taille_groupe                : entier, nullable
taux_remboursement_groupe    : décimal, nullable     # 0 à 1, hors sociétaire évalué
deja_secouru_par_groupe      : booléen, nullable
```

---

## 3. Sortie du scoring — LE contrat central

### `ResultatScoring`
```
score                    : entier          # 300 à 850
tranche                  : enum            # accord | accord_sous_condition |
                                           # comite_de_credit | refus
probabilite_defaut       : décimal         # conservée pour l'audit, PAS affichée telle quelle
montant_recommande       : entier          # FCFA
montant_demande          : entier
mode_calcul              : enum            # socle_seul | enrichi
motif_mode               : optionnel<texte># ex. "primo-emprunteur sans groupe historisé"
decomposition            : liste<ContributionVariable>
points_de_base           : entier
plafond_progressif       : entier          # FCFA, sortie du moteur de crédit progressif
trajectoire_progression  : liste<PalierProgression>   # 3 cycles suivants, si remboursement sans incident
conditions_reexamen      : liste<texte>    # vide si accord simple ; sinon leviers actionnables
version_modele           : texte
version_grille           : texte
horodatage               : date
avertissements           : liste<texte>    # ex. "revenu déclaré absent, valeur imputée"
```

### `PalierProgression`
```
cycle             : entier      # +1, +2, +3
plafond_accessible: entier      # FCFA
```

**`conditions_reexamen` vit dans `ResultatScoring`, pas seulement dans la fiche exportée** :
l'écran E4 l'affiche dès le résultat, avant même que l'agent ne pense à générer un PDF. Voir
`03-MODELE/03-scorecard-et-grille.md` pour la logique de calcul (`decision.py` dans le dépôt de
simulation en est l'implémentation de référence).

### `ContributionVariable`
```
code_variable      : texte      # ex. "nb_mois_avec_depot_12m"
libelle            : texte      # ex. "Régularité de l'épargne"
valeur             : texte      # ex. "11 mois sur 12"
points             : entier     # signé : +31 ou -18
sens               : enum       # favorable | defavorable | neutre
famille            : enum       # profil | activite | epargne | historique | solidaire | demande
explication        : texte      # une phrase en français destinée au sociétaire
```

**Règles sur `decomposition` :**
- Triée par valeur absolue de `points`, décroissante.
- La somme de `points_de_base` et de tous les `points` est **exactement** égale à `score`.
  Un test automatique le vérifie à chaque scoring.
- Le front n'a **aucun** calcul à faire : il affiche.

---

## 4. Fiche de justification

### `FicheJustification`
```
fiche_id             : texte
resultat             : ResultatScoring
societaire_nom       : texte
agence               : texte
agent_nom            : texte
date_edition         : date
facteurs_favorables  : liste<ContributionVariable>    # 3 à 5
facteurs_defavorables: liste<ContributionVariable>    # 3 à 5
conditions_reexamen  : liste<texte>                   # copie de ResultatScoring.conditions_reexamen
mention_legale       : texte
```

---

## 5. Recherche et dossier

### `ResultatRechercheSocietaire`
Un élément de la liste du champ de recherche. Volontairement léger.
```
societaire_id     : texte
nom_complet       : texte
numero_membre     : texte
agence            : texte
zone              : enum
statut            : enum        # actif | inactif | radie
a_credit_en_cours : booléen
```

### `DossierSocietaire`
Vue 360° affichée à l'écran.
```
identite          : IdentiteSocietaire
activite          : ActiviteEconomique
epargne           : SyntheseEpargne
historique_credit : liste<CreditResume>
groupe            : optionnel<SyntheseGroupe>       # segment femme_gie uniquement
alertes           : liste<texte>
```

### `SyntheseEpargne`
Porte la trajectoire dynamique, pas un simple solde — c'est le signal central du score, affiché
en premier sur l'écran E2.
```
solde_moyen_6m       : entier
tendance_12m         : enum         # hausse | stable | erosion
nb_mois_avec_depot_12m: entier      # 0 à 12, alimente la bande visuelle des 12 mois
volatilite           : décimal
ratio_epargne_revenu : décimal
anciennete_relation_mois: entier    # depuis date_adhesion
serie_solde_12m       : liste<PointSolde>   # pour la courbe Recharts
```
```
PointSolde : { mois: date, solde: entier }
```

### `IdentiteSocietaire`
```
societaire_id            : texte
numero_membre            : texte
nom_complet              : texte
segment                  : enum       # salarie | individuel | jeune | femme_gie | agricole
agence                   : texte
date_adhesion            : date
anciennete_mois          : entier
statut                   : enum       # actif | inactif | radie
```

### `ActiviteEconomique`
```
secteur                  : enum
anciennete_activite_mois : entier
revenu_mensuel_declare   : optionnel<entier>
charges_mensuelles       : optionnel<entier>
capacite_remboursement_estimee: entier
```

### `CreditResume`
```
credit_id           : texte
date_deblocage      : date
montant_octroye     : entier
duree_mois          : entier
numero_cycle        : entier
statut              : enum       # en_cours | solde | en_souffrance | radie | restructure
capital_restant_du  : entier
max_jours_retard    : entier
```

### `SyntheseGroupe`
Alimente la carte « Groupe de caution » sur E2, et l'écran E5 en entier — **une liste, pas un
graphe** (ADR-016, `01-ARCHITECTURE/07-strategie-graphe.md`).
```
groupe_id                 : texte
nom_groupe                : texte
taille_actuelle           : entier
date_creation             : date
taux_remboursement_groupe : décimal, nullable   # null si pas d'historique resolu, jamais 0
nb_cycles_completes       : entier
nb_sorties_12m            : entier
statut                    : enum      # actif | dissous | en_difficulte
membres                   : liste<MembreGroupe>   # E5 uniquement, non chargé sur E2
```

### `MembreGroupe`
```
societaire_id     : texte
nom_complet       : texte
role              : enum        # membre | presidente | tresoriere | secretaire
anciennete_mois   : entier
statut_credit     : enum        # aucun_credit | en_cours | solde | en_souffrance
caution_appelee   : booléen     # "déjà secouru", si applicable à ce membre
```

---

## 6. Ports du domaine

Signatures abstraites que les adaptateurs implémentent.

```
LecteurCoreSim
  rechercher_societaires(terme: texte, limite: entier) -> liste<ResultatRechercheSocietaire>
  charger_societaire(id) -> Societaire
  charger_historique_credit(id) -> liste<Credit>
  charger_mouvements_epargne(id, depuis: date) -> liste<MouvementEpargne>
  charger_groupe(id) -> optionnel<GroupeCaution>
  charger_garanties(id) -> liste<Garantie>

FeatureStore
  lire_individuelles(id) -> optionnel<FeaturesIndividuelles>
  lire_solidaires(id) -> optionnel<FeaturesSolidaires>
  ecrire_lot(liste) -> entier
  date_dernier_rafraichissement() -> date

ModeleScoring
  identifiant() -> texte
  version() -> texte
  variables_attendues() -> liste<texte>
  predire(features: dict) -> ProbabiliteDefaut
  contributions(features: dict) -> liste<ContributionBrute>

JournalAudit
  enregistrer_decision(resultat, entree, agent_id) -> texte

GenerateurFiche
  produire_pdf(fiche: FicheJustification) -> flux binaire
```

---

## 7. Conventions HTTP

| Aspect | Règle |
|---|---|
| Préfixe | `/api/v1` |
| Nommage | pluriel, kebab-case : `/societaires`, `/demandes-credit` |
| Corps | JSON, clés en `snake_case` (alignées sur le domaine) |
| Montants | entiers en FCFA, jamais de flottant, jamais de chaîne formatée |
| Dates | ISO 8601 |
| Pagination | `?page=1&taille=20`, réponse `{ elements, total, page, taille }` |
| Erreurs | `{ code, message, details }` — `message` en français, destiné à l'utilisateur |
| Codes | 200, 201, 400 (validation), 401, 403, 404, 409 (conflit métier), 422, 500 |

### Endpoints P0

```
POST /api/v1/auth/connexion
GET  /api/v1/societaires/recherche?terme=...&limite=10
GET  /api/v1/societaires/{id}/dossier
POST /api/v1/scoring
GET  /api/v1/scoring/{id}/fiche
GET  /api/v1/scoring/{id}/fiche.pdf
GET  /api/v1/societaires/{id}/groupe
GET  /api/v1/sante
```

`GET .../groupe` retourne `SyntheseGroupe` avec sa liste `membres` — 404 si le sociétaire n'est
pas du segment `femme_gie` ou n'appartient à aucun groupe actif. Pas d'endpoint « réseau » : il
n'y a pas de structure de graphe à servir (ADR-016).
