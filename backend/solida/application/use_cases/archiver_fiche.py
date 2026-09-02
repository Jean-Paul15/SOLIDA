from dataclasses import dataclass
from datetime import UTC, datetime

from solida.application.use_cases.generer_fiche import GenererFiche
from solida.domain.errors import AccesRefuse
from solida.domain.ports.archivage import FicheRepository
from solida.domain.ports.audit import AuditLog
from solida.domain.ports.fiches_archivees import FicheArchiveeRepository
from solida.domain.ports.generateur_fiche import FichePdfGenerator


@dataclass(frozen=True)
class ArchiverFiche:
    generer_fiche: GenererFiche
    fiche_pdf_generator: FichePdfGenerator
    fiche_repository: FicheRepository
    fiche_archivee_repository: FicheArchiveeRepository
    audit_log: AuditLog

    def execute(
        self,
        decision_id: str,
        archive_par: str,
        agent_role: str,
        agent_agence_id: str | None,
    ) -> str | None:
        fiche_data = self.generer_fiche.execute(decision_id)
        if fiche_data is None:
            return None
        decision, entete = fiche_data
        if agent_role == "agent" and decision.agent_agence_id != agent_agence_id:
            raise AccesRefuse("Cette décision ne concerne pas votre agence.")

        pdf = self.fiche_pdf_generator.generer(decision, entete)
        chemin_objet = f"fiches/{datetime.now(UTC):%Y/%m}/{decision_id}.pdf"
        self.fiche_repository.archiver(chemin_objet, pdf)
        fiche_id = self.fiche_archivee_repository.enregistrer(
            decision_id, chemin_objet, archive_par
        )
        self.audit_log.enregistrer_evenement("fiche_archivee", archive_par, decision_id, {})
        return fiche_id
