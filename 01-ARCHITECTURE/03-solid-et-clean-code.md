# SOLID et clean code appliqués

Les principes énoncés abstraitement ne servent à rien. Chacun est ici traduit en règle vérifiable
avec un exemple tiré de SOLIDA.

---

## S — Responsabilité unique

**Règle :** une classe a une seule raison de changer.

**Application :** on ne fait pas une classe `ServiceScoring` qui lit CORE-SIM, calcule les features,
appelle le modèle, applique la grille, écrit l'audit et rend le PDF. On fait :

| Classe | Change quand… |
|---|---|
| `LecteurCoreSimPostgres` | le schéma du SI de l'IMF change |
| `CalculateurFeaturesIndividuelles` | la liste des variables change |
| `ModeleEbm` | on change de librairie ML |
| `Scorecard` | la formule de mise à l'échelle change |
| `GrilleDecision` | l'institution change ses seuils |
| `JournalAuditPostgres` | le format d'audit change |

**Symptôme d'alerte :** un fichier de plus de 300 lignes, ou dont le nom contient « Manager »,
« Helper », « Utils », « Service » sans complément.

---

## O — Ouvert / fermé

**Règle :** on étend sans modifier.

**Application :** ajouter un troisième modèle (par exemple un GAM alternatif) ne doit modifier aucun
fichier existant. Il suffit d'implémenter le port `ModeleScoring` et de le déclarer dans la
configuration. Le cas d'usage `ScorerDemande` n'est pas touché.

**Test concret :** si ajouter une variante oblige à toucher un `if/elif` central, le principe est
violé.

---

## L — Substitution de Liskov

**Règle :** toute implémentation d'un port est interchangeable sans casser l'appelant.

**Application :** `ModeleSocle` et `ModeleEnrichi` implémentent le même port. La cascade choisit
l'un ou l'autre sans savoir lequel elle manipule. Corollaire : une implémentation ne doit pas
lever une exception que le port ne documente pas, ni exiger des préconditions supplémentaires.

**Piège fréquent :** `FeatureStoreEnMemoire` utilisé en test qui accepte des clés que la version
PostgreSQL rejette. Les tests passent, la production casse.

---

## I — Ségrégation des interfaces

**Règle :** aucun client ne dépend de méthodes qu'il n'utilise pas.

**Application :** on ne crée pas un port `Repository` unique avec vingt méthodes. On crée
`LecteurSocietaire`, `LecteurGroupe`, `LecteurHistoriqueCredit`. Le calculateur d'agrégats
solidaires n'a pas besoin de connaître les mouvements d'épargne.

---

## D — Inversion des dépendances

**Règle :** le domaine définit l'interface, l'infrastructure s'y conforme.

**Application :** le port `LecteurCoreSim` est écrit selon les besoins du domaine, avec un
vocabulaire métier (`recuperer_historique_credit(societaire_id) -> list[Credit]`), et surtout pas
selon le schéma SQL de CORE-SIM. C'est ce qui rend le remplacement par un vrai SI trivial.

---

# Clean code — règles applicables

## Nommage

| Règle | Bon | Mauvais |
|---|---|---|
| Intention, pas implémentation | `taux_remboursement_groupe` | `calc_tr_grp` |
| Pas d'abréviation non standard | `societaire` | `soc`, `sct` |
| Booléen affirmatif | `est_primo_emprunteur` | `pas_nouveau` |
| Domaine en français | `montant_octroye` | `granted_amount` |
| Technique en anglais | `repository`, `handler` | `depot_http` |
| Unité dans le nom | `anciennete_mois`, `montant_fcfa` | `anciennete`, `montant` |

## Fonctions

- Une fonction fait une chose et son nom le dit entièrement.
- Trois paramètres maximum. Au-delà, on passe un objet.
- Pas de paramètre booléen qui pilote deux comportements : faire deux fonctions.
- Profondeur d'indentation maximale : 3. Au-delà, extraire.
- Retour anticipé plutôt qu'imbrication de `else`.

## Argent

**Les montants sont des entiers en FCFA. Jamais de flottant.** Le franc CFA n'a pas de subdivision
utilisée. Un `float` sur un montant est un bug en attente.

## Erreurs

- Exceptions métier dédiées : `SocietaireIntrouvable`, `DonneesInsuffisantes`,
  `ModeleIndisponible`, `GrilleInvalide`.
- Jamais d'`except Exception: pass`.
- Un message d'erreur destiné à l'agent est en français et actionnable :
  « Impossible de calculer le score : le revenu déclaré est absent du dossier. »
  Et non : « ValidationError: field required ».

## Commentaires

Un commentaire justifie un choix non évident, il ne raconte pas ce que le code fait.

```python
# Bon
# Le sexe est chargé pour le contrôle de non-discrimination a posteriori,
# il est explicitement retiré de la matrice avant entraînement (voir 03-MODELE/06).

# Mauvais
# on récupère le sociétaire
societaire = depot.recuperer(id)
```

## Tests

- La logique métier pure est testée en premier, sans dépendance.
- Un test décrit un comportement métier, pas une implémentation :
  `test_un_primo_emprunteur_sans_groupe_est_score_sur_le_socle_seul`.
- Chaque bug corrigé donne lieu à un test qui aurait échoué avant le correctif.
