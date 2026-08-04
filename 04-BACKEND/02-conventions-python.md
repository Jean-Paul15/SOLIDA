# Conventions Python

## Outillage

| Outil | Rôle | Configuration |
|---|---|---|
| **uv** | Gestion des dépendances et de l'environnement | `pyproject.toml`, `uv.lock` versionné |
| **ruff** | Lint et formatage | Remplace black, isort, flake8 |
| **mypy** | Typage statique | `strict = true` sur `domain/` et `application/` |
| **pytest** | Tests | Avec `pytest-cov` |
| **import-linter** | Contrôle des frontières de couches | Règles de `01-ARCHITECTURE/02` |

`uv` est retenu pour sa vitesse d'installation, ce qui compte quand cinq personnes reconstruisent
leur environnement le matin du jour 1.

## Typage

Annotations complètes sur toute fonction publique. `strict` sur le domaine et l'application ;
plus permissif sur les adaptateurs qui manipulent des librairies mal typées.

```python
def calculer_score(
    probabilite: ProbabiliteDefaut,
    parametres: ParametresScorecard,
) -> Score:
```

Interdits : `Any` sans justification écrite, `# type: ignore` sans commentaire expliquant pourquoi.

## Objets valeur

Les concepts métier ne sont pas des types primitifs.

```python
@dataclass(frozen=True)
class Montant:
    """Montant en FCFA. Toujours entier, jamais négatif."""
    valeur: int
```

Cela évite la classe d'erreurs la plus commune sur ce type de projet : passer un montant là où on
attend une durée, ou introduire un flottant dans un calcul monétaire.

## Immutabilité

Les entités du domaine sont `frozen`. Une modification produit une nouvelle instance. Cela
supprime toute une catégorie de bugs de mutation partagée, particulièrement dans le batch.

## Nommage

| Élément | Convention | Exemple |
|---|---|---|
| Module | `snake_case`, français pour le domaine | `scorecard.py`, `cascade.py` |
| Classe | `PascalCase` | `GrilleDecision`, `FeaturesSolidaires` |
| Fonction | `snake_case`, verbe à l'infinitif | `calculer_score`, `charger_societaire` |
| Constante | `SCREAMING_SNAKE_CASE` | `SCORE_MINIMUM` |
| Privé | Préfixe `_` | `_normaliser_nom` |
| Booléen | Préfixe `est_` / `a_` | `est_primo_emprunteur` |

## Docstrings

Sur toute fonction publique du domaine. Format court : ce que fait la fonction, ce qu'elle
suppose, ce qu'elle lève.

```python
def appliquer_grille(score: Score, grille: GrilleDecision) -> Decision:
    """Détermine la tranche et le montant recommandé.

    Suppose que les seuils de la grille sont strictement croissants.
    Lève GrilleInvalide sinon.
    """
```

## Exceptions

Hiérarchie dédiée, jamais d'exception générique.

```python
class ErreurSolida(Exception): ...
class ErreurDomaine(ErreurSolida): ...
class SocietaireIntrouvable(ErreurDomaine): ...
class DonneesInsuffisantes(ErreurDomaine): ...
class InvariantScoreViole(ErreurDomaine): ...
```

Jamais `except Exception: pass`. Jamais d'exception avalée sans journalisation.

## Tests

| Type | Emplacement | Vitesse | Dépendances |
|---|---|---|---|
| Domaine | `tests/domain/` | < 1 s au total | aucune |
| Application | `tests/application/` | < 5 s | doublures |
| Intégration | `tests/integration/` | plus lent | testcontainers |

**Couverture exigée : 100 % sur `domain/rules/`.** Ce sont quelques centaines de lignes qui portent
toute la logique métier ; il n'y a aucune excuse pour ne pas les couvrir entièrement.

Nommage des tests : phrase décrivant le comportement.

```python
def test_un_primo_emprunteur_sans_groupe_bascule_en_mode_socle(): ...
def test_la_somme_des_points_egale_toujours_le_score(): ...
def test_le_taux_de_remboursement_du_groupe_exclut_le_societaire_evalue(): ...
```

## Interdits

| Interdit | Motif |
|---|---|
| `float` pour un montant | Erreurs d'arrondi sur de l'argent |
| Import circulaire | Symptôme de mauvaise découpe |
| Variable globale mutable | Impossible à tester |
| `print` | Utiliser le journal |
| Requête SQL dans le domaine | Violation de couche |
| `datetime.now()` dans le domaine | Le temps est injecté, sinon les tests sont non déterministes |

Le dernier point est important : une règle métier qui appelle `datetime.now()` ne peut pas être
testée sur une date passée, et le rejeu d'une décision devient impossible.
