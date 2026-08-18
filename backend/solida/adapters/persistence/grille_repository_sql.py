from typing import Any

from sqlalchemy import Engine, bindparam, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError

from solida.domain.erreurs import VersionGrilleDejaExistante
from solida.domain.rules.grille import ParametresGrille
from solida.domain.rules.progressif_plafond import ParametresProgressif
from solida.domain.rules.scorecard import ParametresScorecard
from solida.domain.values.grille import ConfigurationGrille
from solida.domain.values.montant import Montant


def _ligne_vers_configuration(ligne: Any) -> ConfigurationGrille:
    seuils = ligne.seuils
    return ConfigurationGrille(
        version_grille=ligne.version_grille,
        grille=ParametresGrille(
            marge=seuils["marge"],
            lgd=seuils["lgd"],
            multiplicateur_accord=seuils["multiplicateur_accord"],
            multiplicateur_vigilance=seuils["multiplicateur_vigilance"],
            multiplicateur_examen=seuils["multiplicateur_examen"],
        ),
        progressif=ParametresProgressif(
            coefficient_progression=seuils["coefficient_progression"],
            montant_plancher=Montant(valeur=seuils["montant_plancher"]),
            plafond_primo_emprunteur=Montant(valeur=seuils["plafond_primo_emprunteur"]),
            plafonds_produits={
                produit_id: Montant(valeur=montant)
                for produit_id, montant in seuils["plafonds_produits"].items()
            },
            modulation_base=seuils["modulation_base"],
            modulation_pente=seuils["modulation_pente"],
            modulation_min=seuils["modulation_min"],
            modulation_max=seuils["modulation_max"],
        ),
        scorecard=ParametresScorecard(
            pdo=ligne.pdo,
            score_reference=ligne.score_reference,
            odds_reference=ligne.odds_reference,
            # Echelle bancaire conventionnelle (300-850, meme convention qu'un score FICO),
            # pas un parametre metier de la cooperative : non stockee dans `seuils`.
            score_min=300,
            score_max=850,
        ),
        auteur=ligne.auteur,
        date_activation=ligne.date_activation,
        active=ligne.active,
    )


def _configuration_vers_seuils(configuration: ConfigurationGrille) -> dict[str, Any]:
    grille, progressif = configuration.grille, configuration.progressif
    return {
        "marge": grille.marge,
        "lgd": grille.lgd,
        "multiplicateur_accord": grille.multiplicateur_accord,
        "multiplicateur_vigilance": grille.multiplicateur_vigilance,
        "multiplicateur_examen": grille.multiplicateur_examen,
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
    }


class SqlGrilleRepository:
    """Implémente `GrilleRepository` contre `grille_decision` (schéma `solida`)."""

    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def lire_active(self) -> ConfigurationGrille:
        requete = text("""
            SELECT * FROM grille_decision WHERE active = true
            ORDER BY date_activation DESC LIMIT 1
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete).one()
        return _ligne_vers_configuration(ligne)

    def enregistrer_nouvelle_version(
        self, configuration: ConfigurationGrille
    ) -> ConfigurationGrille:
        instruction = text("""
            INSERT INTO grille_decision
                (version_grille, seuils, pdo, score_reference, odds_reference,
                 auteur, active)
            VALUES
                (:version_grille, :seuils, :pdo, :score_reference, :odds_reference,
                 :auteur, true)
            RETURNING *
        """).bindparams(bindparam("seuils", type_=JSONB))
        with self._moteur.connect() as connexion:
            try:
                connexion.execute(
                    text("UPDATE grille_decision SET active = false WHERE active = true")
                )
                ligne = connexion.execute(
                    instruction,
                    {
                        "version_grille": configuration.version_grille,
                        "seuils": _configuration_vers_seuils(configuration),
                        "pdo": configuration.scorecard.pdo,
                        "score_reference": configuration.scorecard.score_reference,
                        "odds_reference": configuration.scorecard.odds_reference,
                        "auteur": configuration.auteur,
                    },
                ).one()
            except IntegrityError as erreur:
                # rollback() explicite : sans lui, la connexion reste dans un etat de
                # transaction avortee, reutilise en echec par les appels suivants sur le
                # meme pool jusqu'a ce qu'il soit recycle.
                connexion.rollback()
                raise VersionGrilleDejaExistante(
                    f"La version de grille {configuration.version_grille!r} existe déjà."
                ) from erreur
            connexion.commit()
        return _ligne_vers_configuration(ligne)
