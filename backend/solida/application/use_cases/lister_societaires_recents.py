from dataclasses import dataclass

from solida.domain.ports.audit import AuditLog
from solida.domain.ports.core_sim import LecteurCoreSim
from solida.domain.values.resultat_recherche import ResultatRechercheSocietaire

TYPE_EVENEMENT_CONSULTATION = "consultation_dossier"
LIMITE_PAR_DEFAUT = 5


@dataclass(frozen=True)
class ListerSocietairesRecents:
    """Sociétés distinctes les plus récemment consultées par l'agent — construit à partir
    du journal d'audit, pas d'une table dédiée : c'est déjà une trace qu'on doit garder,
    l'utiliser aussi pour l'écran de recherche n'ajoute aucune donnée nouvelle."""

    lecteur: LecteurCoreSim
    audit_log: AuditLog

    def executer(
        self, agent_id: str, limite: int = LIMITE_PAR_DEFAUT
    ) -> list[ResultatRechercheSocietaire]:
        identifiants = self.audit_log.lister_objets_recents(
            TYPE_EVENEMENT_CONSULTATION, agent_id, limite
        )
        resultats = []
        for societaire_id in identifiants:
            societaire = self.lecteur.charger_societaire(societaire_id)
            if societaire is None:
                continue
            credits = self.lecteur.charger_historique_credit(societaire_id)
            resultats.append(
                ResultatRechercheSocietaire(
                    societaire_id=societaire.societaire_id,
                    nom_complet=societaire.nom_complet,
                    numero_membre=societaire.numero_membre,
                    agence=societaire.agence,
                    zone=societaire.zone,
                    statut="actif",
                    a_credit_en_cours=any(c.statut == "en_cours" for c in credits),
                )
            )
        return resultats
