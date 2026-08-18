from solida.adapters.http.schemas import grille as schema_grille
from solida.domain.values.grille import ConfigurationGrille


def grille_vers_schema(configuration: ConfigurationGrille) -> schema_grille.ConfigurationGrille:
    return schema_grille.ConfigurationGrille(
        version_grille=configuration.version_grille,
        grille=schema_grille.ParametresGrille(
            marge=configuration.grille.marge,
            lgd=configuration.grille.lgd,
            multiplicateur_accord=configuration.grille.multiplicateur_accord,
            multiplicateur_vigilance=configuration.grille.multiplicateur_vigilance,
            multiplicateur_examen=configuration.grille.multiplicateur_examen,
        ),
        progressif=schema_grille.ParametresProgressif(
            coefficient_progression=configuration.progressif.coefficient_progression,
            montant_plancher=configuration.progressif.montant_plancher.valeur,
            plafond_primo_emprunteur=configuration.progressif.plafond_primo_emprunteur.valeur,
            plafonds_produits={
                produit_id: montant.valeur
                for produit_id, montant in configuration.progressif.plafonds_produits.items()
            },
            modulation_base=configuration.progressif.modulation_base,
            modulation_pente=configuration.progressif.modulation_pente,
            modulation_min=configuration.progressif.modulation_min,
            modulation_max=configuration.progressif.modulation_max,
        ),
        scorecard=schema_grille.ParametresScorecard(
            pdo=configuration.scorecard.pdo,
            score_reference=configuration.scorecard.score_reference,
            odds_reference=configuration.scorecard.odds_reference,
        ),
        auteur=configuration.auteur,
        date_activation=configuration.date_activation.isoformat(),
        active=configuration.active,
    )
