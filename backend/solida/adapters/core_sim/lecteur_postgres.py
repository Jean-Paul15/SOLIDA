from datetime import date, timedelta
from typing import Any

from sqlalchemy import Engine, text

from solida.domain.entities.compte_epargne import CompteEpargne
from solida.domain.entities.credit import Credit
from solida.domain.entities.garantie import Garantie
from solida.domain.entities.groupe import GroupeCaution, MembreGroupe
from solida.domain.entities.mouvement_epargne import MouvementEpargne
from solida.domain.entities.societaire import Societaire
from solida.domain.values.resultat_recherche import ResultatRechercheSocietaire

STATUT_SOCIETAIRE_PAR_DEFAUT = "actif"
"""Le générateur ne modélise ni churn ni radiation : voir docs/backend/02-adapters-core-sim.md."""


def _capital_restant_du(
    montant_octroye: int, statut: str, date_deblocage: date, duree_mois: int, aujourdhui: date
) -> int:
    """Approxime le capital restant dû.

    Le générateur produit des crédits bruts (montant, durée, statut) mais pas
    d'échéancier de remboursement détaillé : cette fonction est une estimation
    d'affichage, documentée comme telle, pas un calcul comptable exact.

    `solde` : intégralement remboursé, 0. `en_souffrance` : aucune donnée de
    remboursement partiel n'existe dans le générateur, donc le montant octroyé
    est traité comme intégralement impayé plutôt que d'appliquer un
    amortissement qui suppose, à tort, un remboursement en cours. `en_cours` :
    amortissement linéaire sur la durée écoulée, seule approximation
    raisonnable pour un crédit dont l'issue n'est pas encore connue.
    """
    if statut == "solde":
        return 0
    if statut == "en_souffrance":
        return montant_octroye
    mois_ecoules = max(
        0, (aujourdhui.year - date_deblocage.year) * 12 + aujourdhui.month - date_deblocage.month
    )
    fraction_restante = max(0.0, 1.0 - min(mois_ecoules, duree_mois) / duree_mois)
    return round(montant_octroye * fraction_restante)


def _ligne_vers_credit(ligne: Any, aujourdhui: date) -> Credit:
    date_deblocage: date = ligne.date_deblocage
    duree_mois: int = ligne.duree_mois
    statut: str = ligne.statut
    return Credit(
        credit_id=ligne.credit_id,
        societaire_id=ligne.societaire_id,
        date_deblocage=date_deblocage,
        date_echeance_prevue=ligne.date_issue,
        duree_mois=duree_mois,
        numero_cycle=ligne.numero_cycle,
        montant_octroye=ligne.montant_octroye,
        statut=statut,
        jours_retard_max=(
            None if ligne.jours_retard_max is None else round(ligne.jours_retard_max)
        ),
        capital_restant_du=_capital_restant_du(
            ligne.montant_octroye, statut, date_deblocage, duree_mois, aujourdhui
        ),
    )


class LecteurCoreSimPostgres:
    """Implémentation du port `LecteurCoreSim` contre le schéma réel produit
    par `simulateur/`. Connexion via le rôle `solida_lecteur` (lecture seule)."""

    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def rechercher_societaires(
        self, terme: str, limite: int
    ) -> list[ResultatRechercheSocietaire]:
        requete = text("""
            SELECT s.societaire_id, s.nom_complet, s.numero_membre, s.caisse_id, s.zone,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s
            WHERE s.nom_complet ILIKE '%' || :terme || '%' OR s.numero_membre = :terme
            ORDER BY similarity(s.nom_complet, :terme) DESC
            LIMIT :limite
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"terme": terme, "limite": limite})
            return [
                ResultatRechercheSocietaire(
                    societaire_id=ligne.societaire_id,
                    nom_complet=ligne.nom_complet,
                    numero_membre=ligne.numero_membre,
                    agence=ligne.caisse_id,
                    zone=ligne.zone,
                    statut=STATUT_SOCIETAIRE_PAR_DEFAUT,
                    a_credit_en_cours=bool(ligne.a_credit_en_cours),
                )
                for ligne in lignes
            ]

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        requete = text("""
            SELECT societaire_id, numero_membre, nom_complet, caisse_id, date_adhesion,
                   anciennete_societaire_mois, segment, age, zone, nb_personnes_a_charge,
                   niveau_education, parts_sociales, revenu_declare, gie_id
            FROM societaires WHERE societaire_id = :id
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete, {"id": societaire_id}).first()
        if ligne is None:
            return None
        return Societaire(
            societaire_id=ligne.societaire_id,
            numero_membre=ligne.numero_membre,
            nom_complet=ligne.nom_complet,
            agence=ligne.caisse_id,
            date_adhesion=ligne.date_adhesion,
            anciennete_mois=ligne.anciennete_societaire_mois,
            segment=ligne.segment,
            age=ligne.age,
            zone=ligne.zone,
            nb_personnes_a_charge=ligne.nb_personnes_a_charge,
            niveau_instruction=ligne.niveau_education,
            parts_sociales_montant=ligne.parts_sociales,
            revenu_mensuel_declare=(
                None if ligne.revenu_declare is None else round(ligne.revenu_declare)
            ),
            groupe_id=ligne.gie_id,
        )

    def charger_historique_credit(self, societaire_id: str) -> list[Credit]:
        requete = text("""
            SELECT credit_id, societaire_id, date_deblocage, date_issue, duree_mois,
                   numero_cycle, montant_octroye, statut, jours_retard_max
            FROM credits WHERE societaire_id = :id ORDER BY date_deblocage DESC
        """)
        aujourdhui = date.today()
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id})
            return [_ligne_vers_credit(ligne, aujourdhui) for ligne in lignes]

    def charger_compte_epargne(self, societaire_id: str) -> CompteEpargne | None:
        requete = text("""
            SELECT compte_id, societaire_id, solde_epargne_moyen_6m, nb_mois_avec_depot_12m,
                   croissance_epargne_12m, volatilite_epargne
            FROM comptes_epargne WHERE societaire_id = :id
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete, {"id": societaire_id}).first()
        if ligne is None:
            return None
        return CompteEpargne(
            compte_id=ligne.compte_id,
            societaire_id=ligne.societaire_id,
            solde_moyen_6m=round(ligne.solde_epargne_moyen_6m),
            nb_mois_avec_depot_12m=ligne.nb_mois_avec_depot_12m,
            croissance_12m=float(ligne.croissance_epargne_12m),
            volatilite=float(ligne.volatilite_epargne),
        )

    def charger_mouvements_epargne(
        self, societaire_id: str, depuis: date
    ) -> list[MouvementEpargne]:
        requete = text("""
            SELECT m.mouvement_id, m.compte_id, m.date_operation, m.sens, m.montant
            FROM mouvements_epargne m
            JOIN comptes_epargne c ON c.compte_id = m.compte_id
            WHERE c.societaire_id = :id AND m.date_operation >= :depuis
            ORDER BY m.date_operation
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id, "depuis": depuis})
            return [
                MouvementEpargne(
                    mouvement_id=ligne.mouvement_id,
                    compte_id=ligne.compte_id,
                    date_operation=ligne.date_operation,
                    sens=ligne.sens,
                    montant=round(ligne.montant),
                )
                for ligne in lignes
            ]

    def charger_garanties(self, societaire_id: str) -> list[Garantie]:
        requete = text("""
            SELECT garantie_id, credit_id, type_garantie, garant_societaire_id,
                   beneficiaire_societaire_id, montant_garanti, date_engagement, garantie_appelee
            FROM garanties
            WHERE beneficiaire_societaire_id = :id OR garant_societaire_id = :id
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(requete, {"id": societaire_id})
            return [
                Garantie(
                    garantie_id=ligne.garantie_id,
                    credit_id=ligne.credit_id,
                    type_garantie=ligne.type_garantie,
                    garant_societaire_id=ligne.garant_societaire_id,
                    beneficiaire_societaire_id=ligne.beneficiaire_societaire_id,
                    montant_garanti=round(ligne.montant_garanti),
                    date_engagement=ligne.date_engagement,
                    garantie_appelee=bool(ligne.garantie_appelee),
                )
                for ligne in lignes
            ]

    def charger_groupe(self, societaire_id: str) -> GroupeCaution | None:
        requete_appartenance = text("""
            SELECT gie_id FROM societaires WHERE societaire_id = :id AND gie_id IS NOT NULL
        """)
        with self._moteur.connect() as connexion:
            ligne = connexion.execute(requete_appartenance, {"id": societaire_id}).first()
            if ligne is None:
                return None
            gie_id = ligne.gie_id

            groupe_ligne = connexion.execute(
                text(
                    "SELECT gie_id, taille, date_creation FROM groupes_gie WHERE gie_id = :gie_id"
                ),
                {"gie_id": gie_id},
            ).first()
            if groupe_ligne is None:
                return None

            membres_lignes = connexion.execute(
                text("""
                    SELECT a.societaire_id, s.nom_complet, a.role, a.date_entree, a.date_sortie
                    FROM appartenances_gie a
                    JOIN societaires s ON s.societaire_id = a.societaire_id
                    WHERE a.gie_id = :gie_id
                """),
                {"gie_id": gie_id},
            ).all()

            statuts_credit = connexion.execute(
                text("""
                    SELECT DISTINCT ON (societaire_id) societaire_id, statut
                    FROM credits
                    WHERE societaire_id = ANY(:ids)
                    ORDER BY societaire_id, date_deblocage DESC
                """),
                {"ids": [m.societaire_id for m in membres_lignes]},
            ).all()
            statut_par_societaire = {s.societaire_id: s.statut for s in statuts_credit}

            cautions_appelees = connexion.execute(
                text("""
                    SELECT DISTINCT garant_societaire_id
                    FROM garanties
                    WHERE garant_societaire_id = ANY(:ids) AND garantie_appelee = true
                """),
                {"ids": [m.societaire_id for m in membres_lignes]},
            ).all()
            garants_appeles = {c.garant_societaire_id for c in cautions_appelees}

            autres_membres_ids = [
                m.societaire_id for m in membres_lignes if m.societaire_id != societaire_id
            ]
            credits_resolus = connexion.execute(
                text("""
                    SELECT statut FROM credits
                    WHERE societaire_id = ANY(:ids) AND statut IN ('solde', 'en_souffrance')
                """),
                {"ids": autres_membres_ids},
            ).all()
            nb_sortie_12m = connexion.execute(
                text("""
                    SELECT count(*) AS n FROM appartenances_gie
                    WHERE gie_id = :gie_id AND date_sortie >= :depuis
                """),
                {"gie_id": gie_id, "depuis": date.today() - timedelta(days=365)},
            ).scalar_one()

        nb_resolus = len(credits_resolus)
        nb_soldes = sum(1 for c in credits_resolus if c.statut == "solde")
        taux_remboursement = (nb_soldes / nb_resolus) if nb_resolus > 0 else None
        taille_active = sum(1 for m in membres_lignes if m.date_sortie is None)

        statut_groupe = "actif"
        if taille_active == 0:
            statut_groupe = "dissous"
        elif taux_remboursement is not None and taux_remboursement < 0.5:
            statut_groupe = "en_difficulte"

        aujourdhui = date.today()
        membres = [
            MembreGroupe(
                societaire_id=m.societaire_id,
                nom_complet=m.nom_complet,
                role=m.role,
                anciennete_mois=(aujourdhui.year - m.date_entree.year) * 12
                + aujourdhui.month
                - m.date_entree.month,
                statut_credit=statut_par_societaire.get(m.societaire_id, "aucun_credit"),
                caution_appelee=m.societaire_id in garants_appeles,
            )
            for m in membres_lignes
            if m.date_sortie is None
        ]

        return GroupeCaution(
            groupe_id=groupe_ligne.gie_id,
            nom_groupe=f"Groupement {groupe_ligne.gie_id}",
            taille_actuelle=taille_active,
            date_creation=groupe_ligne.date_creation,
            taux_remboursement_groupe=taux_remboursement,
            nb_cycles_completes=nb_soldes,
            nb_credits_anterieurs_soldes=nb_soldes,
            nb_sorties_12m=nb_sortie_12m,
            statut=statut_groupe,
            membres=membres,
        )
