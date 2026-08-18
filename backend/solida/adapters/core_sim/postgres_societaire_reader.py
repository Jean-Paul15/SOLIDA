from sqlalchemy import Engine, text

from solida.domain.entities.societaire import Societaire
from solida.domain.values.resultat_recherche import ResultatRechercheSocietaire

STATUT_SOCIETAIRE_PAR_DEFAUT = "actif"
"""Le générateur ne modélise ni churn ni radiation : voir docs/backend/02-adapters-core-sim.md."""


class PostgresSocietaireReader:
    def __init__(self, moteur: Engine) -> None:
        self._moteur = moteur

    def rechercher_societaires(
        self, terme: str, limite: int, agence_id: str | None = None
    ) -> list[ResultatRechercheSocietaire]:
        requete = text("""
            SELECT s.societaire_id, s.nom_complet, s.numero_membre, s.caisse_id, s.zone,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s
            WHERE (s.nom_complet ILIKE '%' || :terme || '%' OR s.numero_membre = :terme)
              AND (CAST(:agence_id AS text) IS NULL OR s.caisse_id = :agence_id)
            ORDER BY similarity(s.nom_complet, :terme) DESC
            LIMIT :limite
        """)
        with self._moteur.connect() as connexion:
            lignes = connexion.execute(
                requete, {"terme": terme, "limite": limite, "agence_id": agence_id}
            )
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

    def compter_societaires(self, terme: str, agence_id: str | None = None) -> int:
        requete = text("""
            SELECT count(*) FROM societaires s
            WHERE (s.nom_complet ILIKE '%' || :terme || '%' OR s.numero_membre = :terme)
              AND (CAST(:agence_id AS text) IS NULL OR s.caisse_id = :agence_id)
        """)
        with self._moteur.connect() as connexion:
            return connexion.execute(requete, {"terme": terme, "agence_id": agence_id}).scalar_one()

    def charger_societaire(self, societaire_id: str) -> Societaire | None:
        requete = text("""
            SELECT s.societaire_id, s.numero_membre, s.nom_complet, s.caisse_id, s.date_adhesion,
                   s.anciennete_societaire_mois, s.segment, s.age, s.zone, s.nb_personnes_a_charge,
                   s.niveau_education, s.parts_sociales, s.revenu_declare, s.gie_id,
                   EXISTS (
                       SELECT 1 FROM credits c
                       WHERE c.societaire_id = s.societaire_id AND c.statut = 'en_cours'
                   ) AS a_credit_en_cours
            FROM societaires s WHERE s.societaire_id = :id
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
            a_credit_en_cours=bool(ligne.a_credit_en_cours),
        )
