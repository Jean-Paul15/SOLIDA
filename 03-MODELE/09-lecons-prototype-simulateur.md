# Leçons du prototype simulateur (retiré)

## Contexte

`simulateur/simulateur/features.py`, `valider.py` et `decision.py` formaient un prototype
jetable, écrit en même temps que le générateur CORE-SIM (`pipeline.py`), pour prouver —
avant que le vrai modèle et le vrai backend n'existent — que les données synthétiques
produisent un signal plausible. Ils ont été supprimés : leur rôle de démonstration est
rempli, ce qu'ils faisaient correctement est déjà spécifié ailleurs en mieux, et ils
comportaient des écarts qui les rendaient trompeurs à laisser traîner sans mainteneur.

Ce fichier n'est pas une spécification supplémentaire : c'est la trace de ce que ces
trois fichiers voulaient démontrer, et de ce qui a concrètement échoué dans leur
implémentation — pour que personne ne reproduise les mêmes écarts en construisant le
vrai pipeline de feature engineering / entraînement.

## Ce que chacun visait, et où c'est traité maintenant

| Prototype | Visait à démontrer | Traité maintenant dans |
|---|---|---|
| `features.py` | Trois blocs SOCLE / SOLIDAIRE / SECTORIEL, toutes variables calculées à la date de déblocage | `02-feature-engineering.md` (règle absolue en tête de fichier) |
| `valider.py` | Performance émergente (jamais ciblée), fourchette AUC de sanité, matrice d'argent, gain de la couche solidaire sur la seule population éligible | `05-evaluation-et-metriques.md`, `03-scorecard-et-grille.md` (matrice de coûts) |
| `decision.py` | Grille de décision issue de la matrice de coûts, plafond de crédit progressif, conditions de réexamen actionnables | `03-scorecard-et-grille.md` ; implémenté réellement dans `backend/solida/domain/rules/progressif.py` et `grille.py` |

Ces principes restent valides. Ce qui suit est ce que le prototype n'a **pas** réussi à
respecter, malgré ses propres commentaires affirmant le contraire.

## Ce qui a échoué — à ne pas reproduire

### 1. Fuite temporelle du bloc épargne

`features.py` affirmait dans son propre docstring : *« Toutes les variables derivees sont
LEAK-FREE (calculees a la date de deblocage) »*. Faux pour l'épargne : `comptes_epargne`
n'a qu'une seule ligne par sociétaire (un instantané « à aujourd'hui »), jointe telle
quelle sur **chaque** crédit historique du même sociétaire, y compris ceux d'il y a
plusieurs années. `gen_garanties` (générateur) faisait la même chose pour le montant
d'épargne nantie. Avec un découpage train/test **temporel** (`valider.py`), l'instantané
figé est structurellement plus proche de la vérité pour les crédits récents (test) que
pour les vieux crédits (train) — un biais qui peut gonfler l'AUC apparente sans que la
fourchette de sanité (0,70–0,85) ne le révèle.

**La règle qui protège de ça est déjà énoncée** en tête de `02-feature-engineering.md` :
*« Toute feature est calculée à une `date_reference`, qui est la date de la demande de
crédit. Jamais à la date d'aujourd'hui. »* Le futur pipeline de feature engineering doit
soit disposer d'un historique d'épargne daté (pas un instantané unique) pour calculer
chaque variable à la vraie date de référence, soit n'entraîner que sur les crédits assez
récents pour que l'approximation soit défendable — un choix à trancher explicitement,
pas à laisser implicite dans un `join`.

### 2. Coefficient documenté comme protecteur, jamais câblé

`config.yaml` du générateur documentait `coef_ratio_garantie: 0.55` comme facteur
protecteur du risque (« ratio épargne nantie / crédit »). Il n'était référencé **nulle
part** dans la formule de génération du défaut. Résultat : `ratio_garantie`, une variable
du socle, n'avait aucun lien causal réel avec le défaut dans la vérité synthétique —
seulement des corrélations croisées fortuites. Pire, `decision.py` s'en servait pour
conseiller au sociétaire de renforcer son épargne nantie comme levier actionnable, un
conseil fondé sur une variable qui n'était prédictive que par accident dans les données
d'entraînement.

**Leçon** : chaque coefficient d'un générateur de données synthétiques qui prétend
représenter un effet métier documenté doit être vérifié comme effectivement appliqué dans
la formule de génération — un coefficient orphelin dans la config n'est pas neutre, il
crée une variable qui semble informative mais ne l'est pas dans la vérité qu'on a
fabriquée.

### 3. Formule d'échéance simplifiée à l'excès, code mort laissé en place

Le générateur de crédits calculait une échéance dépendante du taux d'intérêt configuré,
puis l'écrasait immédiatement par un forfait de 10 % ignorant la durée et le taux — les
deux lignes contradictoires étaient restées côte à côte, signe d'un refactor abandonné en
cours de route. Un crédit de 3 mois et un de 24 mois recevaient donc la même charge
relative, ce qui alimentait `endettement`, donc la formule de risque, avec un signal
appauvri.

**Leçon** : ne pas laisser une formule remplacée en place « au cas où » — soit elle est
vraie et utilisée, soit elle est supprimée. Le doute qu'elle laisse (quelle est la bonne
version ?) coûte plus cher qu'elle ne rapporte.

## Pour la suite

Le vrai pipeline de feature engineering et d'entraînement (encore à construire derrière
le port `ModeleScoring`, voir `docs/backend/03-decisions-provisoires-a-revoir.md`) doit
partir des spécifications de `03-MODELE/`, pas de ces trois fichiers. S'il a besoin d'un
harnais de validation jetable pour itérer vite, le reconstruire en respectant dès le
départ la règle leak-free et la checklist de `05-evaluation-et-metriques.md` — pas en
relisant `valider.py` dans l'historique git comme modèle à copier.
