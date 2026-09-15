from typing import Any

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError

from solida.domain.errors import VersionGrilleDejaExistante
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant


def _row_to_configuration(row: Any) -> ConfigurationGrille:
    thresholds = row.seuils
    return ConfigurationGrille(
        version_grille=row.version_grille,
        grille=ParametresGrille(
            marge=thresholds["marge"],
            lgd=thresholds["lgd"],
            multiplicateur_accord=thresholds["multiplicateur_accord"],
            plafond_institutionnel_fcfa=thresholds["plafond_institutionnel_fcfa"],
            ratio_endettement_maximal=thresholds["ratio_endettement_maximal"],
        ),
        progressif=ParametresProgressif(
            coefficient_progression=thresholds["coefficient_progression"],
            montant_plancher=Montant(valeur=thresholds["montant_plancher"]),
            plafond_primo_emprunteur=Montant(valeur=thresholds["plafond_primo_emprunteur"]),
            plafonds_produits={
                produit_id: Montant(valeur=montant)
                for produit_id, montant in thresholds["plafonds_produits"].items()
            },
            modulation_base=thresholds["modulation_base"],
            modulation_pente=thresholds["modulation_pente"],
            modulation_min=thresholds["modulation_min"],
            modulation_max=thresholds["modulation_max"],
        ),
        scorecard=ParametresScorecard(
            pdo=row.pdo,
            score_reference=row.score_reference,
            odds_reference=row.odds_reference,
            # Échelle bancaire fixe, non stockée dans les seuils métier.
            score_min=300,
            score_max=850,
        ),
        auteur=row.auteur,
        date_activation=row.date_activation,
        active=row.active,
        classification_objets=dict(thresholds["classification_objets"]),
        objets_implicites_produits=dict(thresholds["objets_implicites_produits"]),
    )


def _configuration_to_thresholds(configuration: ConfigurationGrille) -> dict[str, Any]:
    grille, progressif = configuration.grille, configuration.progressif
    return {
        "marge": grille.marge,
        "lgd": grille.lgd,
        "multiplicateur_accord": grille.multiplicateur_accord,
        "plafond_institutionnel_fcfa": grille.plafond_institutionnel_fcfa,
        "ratio_endettement_maximal": grille.ratio_endettement_maximal,
        "coefficient_progression": progressif.coefficient_progression,
        "montant_plancher": progressif.montant_plancher.valeur,
        "plafond_primo_emprunteur": progressif.plafond_primo_emprunteur.valeur,
        "plafonds_produits": {
            produit_id: montant.valeur
            for produit_id, montant in progressif.plafonds_produits.items()
        },
        "modulation_base": progressif.modulation_base,
        "modulation_pente": progressif.modulation_pente,
        "modulation_min": progressif.modulation_min,
        "modulation_max": progressif.modulation_max,
        "classification_objets": dict(configuration.classification_objets),
        "objets_implicites_produits": dict(configuration.objets_implicites_produits),
    }


class SqlGrilleRepository:
    """Implémente `GrilleRepository` contre `grille_decision` (schéma `solida`)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def lire_active(self) -> ConfigurationGrille:
        query = text("""
            SELECT * FROM grille_decision WHERE active = true
            ORDER BY date_activation DESC LIMIT 1
        """)
        with self._engine.connect() as connection:
            row = connection.execute(query).one()
        return _row_to_configuration(row)

    def enregistrer_nouvelle_version(
        self, configuration: ConfigurationGrille
    ) -> ConfigurationGrille:
        insert_statement = text("""
            INSERT INTO grille_decision
                (version_grille, seuils, pdo, score_reference, odds_reference,
                 auteur, active)
            VALUES
                (:version_grille, :seuils, :pdo, :score_reference, :odds_reference,
                 :auteur, true)
            RETURNING *
        """).bindparams(bindparam("seuils", type_=JSONB))
        with self._engine.connect() as connection:
            try:
                connection.execute(
                    text("UPDATE grille_decision SET active = false WHERE active = true")
                )
                row = connection.execute(
                    insert_statement,
                    {
                        "version_grille": configuration.version_grille,
                        "seuils": _configuration_to_thresholds(configuration),
                        "pdo": configuration.scorecard.pdo,
                        "score_reference": configuration.scorecard.score_reference,
                        "odds_reference": configuration.scorecard.odds_reference,
                        "auteur": configuration.auteur,
                    },
                ).one()
            except IntegrityError as error:
                # Réinitialise la connexion avant de la rendre au pool.
                connection.rollback()
                raise VersionGrilleDejaExistante(
                    f"La version de grille {configuration.version_grille!r} existe déjà."
                ) from error
            connection.commit()
        return _row_to_configuration(row)
