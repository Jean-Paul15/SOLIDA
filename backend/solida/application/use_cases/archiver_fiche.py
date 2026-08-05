from dataclasses import dataclass
from datetime import UTC, datetime

from solida.application.use_cases.generer_fiche import GenererFiche
from solida.domain.erreurs import AccesRefuse
from solida.domain.ports.archivage import DepotFiches
from solida.domain.ports.audit import JournalAudit
from solida.domain.ports.fiches_archivees import DepotFichesArchivees
from solida.domain.ports.generateur_fiche import GenerateurFichePdf


@dataclass(frozen=True)
class ArchiverFiche:
    generer_fiche: GenererFiche
    generateur_pdf: GenerateurFichePdf
    depot_fiches: DepotFiches
    depot_fiches_archivees: DepotFichesArchivees
    journal_audit: JournalAudit

    def executer(
        self,
        decision_id: str,
        archive_par: str,
        agent_role: str,
        agent_agence_id: str | None,
    ) -> str | None:
        resultat = self.generer_fiche.executer(decision_id)
        if resultat is None:
            return None
        decision, entete = resultat
        if agent_role == "agent" and decision.agent_agence_id != agent_agence_id:
            raise AccesRefuse("Cette décision ne concerne pas votre agence.")

        pdf = self.generateur_pdf.generer(decision, entete)
        chemin_objet = f"fiches/{datetime.now(UTC):%Y/%m}/{decision_id}.pdf"
        self.depot_fiches.archiver(chemin_objet, pdf)
        fiche_id = self.depot_fiches_archivees.enregistrer(decision_id, chemin_objet, archive_par)
        self.journal_audit.enregistrer_evenement("fiche_archivee", archive_par, decision_id, {})
        return fiche_id
