from datetime import date, timedelta

from sqlalchemy import Engine, text

from solida.domain.entities.groupe import GroupeCaution, MembreGroupe


class PostgresGroupeReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

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
