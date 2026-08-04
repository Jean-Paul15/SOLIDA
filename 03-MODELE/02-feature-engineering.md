# Feature engineering

## Règle absolue

**Toute feature est calculée à une `date_reference`**, qui est la date de la demande de crédit.
Jamais à la date d'aujourd'hui. Cette contrainte apparaît dans la signature de toutes les
fonctions de calcul. Voir `02-DONNEES/05` sur les fuites.

## Variables du socle individuel

| Code | Libellé métier | Calcul | Famille |
|---|---|---|---|
| `age` | Âge | Années à la date de référence | profil |
| `anciennete_societaire_mois` | Ancienneté de sociétariat | Depuis l'adhésion | profil |
| `nb_personnes_a_charge` | Personnes à charge | Déclaratif | profil |
| `zone_residence` | Zone | Catégoriel | profil |
| `secteur_activite` | Secteur | Catégoriel | activité |
| `anciennete_activite_mois` | Ancienneté de l'activité | Déclaratif | activité |
| `revenu_mensuel_declare` | Revenu déclaré | Déclaratif | activité |
| `ratio_endettement` | Taux d'endettement | Échéance estimée / revenu net | demande |
| `solde_epargne_moyen_6m` | Épargne moyenne | Moyenne des soldes mensuels | épargne |
| `nb_mois_avec_depot_12m` | Régularité de l'épargne | Nombre de mois avec ≥ 1 dépôt | épargne |
| `tendance_epargne_12m` | Trajectoire | Solde en hausse / stable / en érosion sur 12 mois | épargne |
| `volatilite_epargne` | Volatilité de l'épargne | Écart-type / moyenne des soldes | épargne |
| `ratio_epargne_revenu` | Effort d'épargne | Épargne moyenne / revenu déclaré | épargne |
| `anciennete_epargne_mois` | Ancienneté de la relation d'épargne | Depuis `date_adhesion`, à la date de la demande | épargne |
| `ratio_epargne_montant` | Épargne rapportée au montant | Épargne moyenne / montant demandé (ratio de garantie) | épargne |
| `segment` | Segment du sociétaire | salarié, individuel, jeune, femme_gie, agricole — catégoriel, disponible dès l'adhésion | profil |
| `nb_credits_anterieurs` | Crédits antérieurs | Comptage, strictement avant | historique |
| `nb_incidents_anterieurs` | Incidents antérieurs | Retards > seuil | historique |
| `max_jours_retard_historique` | Pire retard | Maximum observé | historique |
| `montant_max_rembourse` | Plus gros crédit soldé | Maximum des crédits soldés sans incident | historique |
| `numero_cycle` | Cycle | Rang du crédit | historique |
| `ratio_montant_historique` | Progression demandée | Montant demandé / montant max remboursé | demande |
| `parts_sociales_montant` | Parts sociales | Capital souscrit | profil |
| `duree_demandee_mois` | Durée | Saisie | demande |
| `objet_credit` | Objet | Catégoriel | demande |

**`ratio_montant_historique` est une variable importante et souvent oubliée.** Un sociétaire qui
demande huit fois le montant qu'il a déjà remboursé présente un risque différent de celui qui
demande 1,3 fois. C'est exactement la logique du crédit progressif, rendue quantitative.

**La trajectoire d'épargne est le signal central, pas le solde.** `tendance_epargne_12m`,
`ratio_epargne_revenu` et `anciennete_epargne_mois` valent davantage qu'un solde moyen isolé : dans
le modèle mutualiste, l'épargne est la porte d'entrée du crédit, donc disponible pour **100 % du
portefeuille**, y compris un primo-emprunteur sans historique de crédit. C'est cette lecture
dynamique, pas la position dans un réseau, qui porte l'essentiel du signal (voir
`03-MODELE/07-notebook-construction.md`, comparatif socle / solidaire / sectoriel).

## Variables de la couche solidaire (segment de groupe)

Voir `01-ARCHITECTURE/07-strategie-graphe.md` (ADR-016) pour la justification : ces variables sont
des **agrégats SQL simples** sur le segment des crédits de groupe, jamais des métriques de graphe.

| Code | Libellé métier | Calcul |
|---|---|---|
| `en_groupe` | Appartenance à un groupe de crédit | Booléen — faux pour la majorité du portefeuille (crédit individuel) |
| `taille_groupe` | Taille du groupe | Membres actifs à la date |
| `taux_remboursement_groupe` | Réputation du groupe | Crédits du groupe soldés sans incident, **hors sociétaire évalué** |
| `deja_secouru_par_groupe` | Garantie déjà appelée à son profit | Booléen |

**Le retrait du sociétaire évalué du calcul de `taux_remboursement_groupe` est impératif.** Sans
cela, on lui prédit son propre défaut et le modèle paraît excellent avant de s'effondrer.

**Volontairement écartées (ADR-016) :** `degre_garant`, `degre_beneficiaire`,
`taux_defaut_voisinage`, `centralite_intermediarite`, `score_reputation_propage`. Ces métriques de
graphe supposent une densité de réseau que la structure réelle d'un portefeuille de crédit
individuel dominant ne présente pas ; les calculer produirait un signal essentiellement bruité.

**Note d'agent (ADR-017) :** un champ `note_agent` existe dans le schéma comme **option
désactivée**. La littérature le confirme prédictif, mais il n'est presque jamais un champ structuré
dans un système de gestion de microfinance. Il n'entre dans le modèle que si un praticien confirme
sa saisie structurée dans le SI de la coopérative.

## Ce que nous ne faisons pas

| Écarté | Motif |
|---|---|
| Croisements automatiques massifs | L'EBM détecte les interactions utiles seul |
| Variables issues d'un texte libre | Pas de champ texte fiable dans un SI d'IMF |
| Encodage par la cible (`target encoding`) | Fuite trop facile, gain faible |
| Normalisation | Inutile pour un modèle par arbres, et nuit à l'interprétation des points |
| Réduction de dimension (ACP) | Détruit l'interprétabilité, qui est la raison d'être du projet |

## Traitement des catégories

Modalités rares (< 1 % des observations) regroupées dans `autre`. Sans cela, une modalité vue
trois fois produit une fonction de forme instable et un nombre de points aberrant sur un dossier
isolé.

## Documentation obligatoire

Chaque feature est décrite dans un catalogue versionné : code, libellé métier destiné à
l'affichage, famille, formule, unité, plage attendue, traitement de l'absence, phrase
d'explication en français pour la fiche de justification.

Ce catalogue est la source unique. Le front, la fiche PDF et le modèle lisent le même libellé,
ce qui garantit qu'un agent, un sociétaire et un auditeur voient exactement le même mot pour
désigner la même chose.

## Variables de conditions sectorielles (micro-économie observée) — P1/P2

Ces variables captent la santé économique récente du secteur du sociétaire, **sans donnée externe
et sans hypothèse de calendrier agricole** (voir ADR-014). Elles sont calculées sur le portefeuille
propre de l'IMF, sur une fenêtre glissante se terminant **strictement avant la date de référence**.

| Code | Libellé métier | Calcul |
|---|---|---|
| `secteur_tendance_impayes` | Tension récente du secteur | Taux de défaut du secteur sur 3-6 mois, en **écart à sa propre base** de moyen terme |
| `secteur_velocite_remboursement` | Régularité récente du secteur | Part d'échéances payées à temps dans le secteur récemment |
| `secteur_dynamique_epargne` | Stress d'épargne du secteur | Flux net d'épargne du secteur (un retrait net est un signal avancé de stress) |
| `secteur_acceleration` | Bascule du secteur | Variation de la tendance : le secteur se dégrade-t-il ou se rétablit-il |
| `zone_secteur_tendance_impayes` | Tension locale | Même logique, croisée zone × secteur |

**Principes impératifs :**

- **Adaptatif, jamais calendaire.** Aucune de ces variables ne suppose un mois de semis. On observe
  ce que le portefeuille montre aujourd'hui.
- **Écart à la base, pas niveau absolu.** On mesure « ce secteur va plus mal que d'habitude », pas
  « ce secteur est structurellement risqué », pour ne pas pénaliser deux fois un secteur pauvre.
- **Rétrécissement (shrinkage) vers une base globale** pour les secteurs et zones à faible effectif,
  plus un seuil d'effectif minimal. En dessous : `null`, jamais `0`.
- **Anti-fuite.** Fenêtre se terminant avant la date de la demande ; le crédit évalué n'entre jamais
  dans le calcul de la tendance de son propre secteur.
- **Poids borné.** Ces variables informent surtout le montant recommandé et les conditions, pas un
  refus binaire. La procyclicité est ainsi contenue (voir `06-ethique-et-non-discrimination.md`).
- **Surveillance d'équité.** Le taux d'approbation par secteur et par zone est suivi dans le temps ;
  ces variables passent sous le contrôle de non-discrimination par zone.

**Périmètre :** P1 pour la tendance d'impayés et la dynamique d'épargne du secteur ; P2 pour
l'accélération et le croisement zone × secteur. À valider avec les experts métier avant construction
du modèle.
