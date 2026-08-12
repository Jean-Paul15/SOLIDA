from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status

from solida.adapters.http import mappers
from solida.adapters.http.schemas.societaires import DossierSocietaire, ResultatRechercheSocietaire
from solida.adapters.persistence.journal_audit_sql import JournalAuditSql
from solida.adapters.persistence.modeles_sqlalchemy import Utilisateur
from solida.application.use_cases.consulter_dossier import ConsulterDossier
from solida.application.use_cases.lister_societaires_recents import ListerSocietairesRecents
from solida.application.use_cases.rechercher_societaire import RechercherSocietaire
from solida.domain.erreurs import AccesRefuse
from solida.infrastructure.auth import current_active_user
from solida.infrastructure.dependances import (
    consulter_dossier,
    journal_audit,
    lister_societaires_recents,
    rechercher_societaire,
)

routeur = APIRouter(prefix="/api/v1/societaires", tags=["societaires"])


def _agence_agent(utilisateur: Utilisateur) -> str | None:
    """`None` pour tout rôle qui n'est pas cloisonné par agence : `agent` seulement."""
    return utilisateur.agence_id if utilisateur.role == "agent" else None


@routeur.get("/recherche")
def rechercher(
    terme: str = "",
    # Plafond serveur : un compte superviseur/auditeur/administrateur n'est pas cloisonne par
    # agence, `limite` doit donc etre borne independamment de ce que le client demande.
    limite: int = Query(default=10, le=50),
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: RechercherSocietaire = Depends(rechercher_societaire),
) -> dict[str, object]:
    resultats = cas_usage.executer(terme, limite, _agence_agent(utilisateur))
    return {
        "elements": [ResultatRechercheSocietaire.model_validate(asdict(r)) for r in resultats],
        "total": len(resultats),
    }


@routeur.get("/recents")
def recents(
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: ListerSocietairesRecents = Depends(lister_societaires_recents),
) -> dict[str, object]:
    resultats = cas_usage.executer(str(utilisateur.id))
    return {"elements": [ResultatRechercheSocietaire.model_validate(asdict(r)) for r in resultats]}


@routeur.get("/{societaire_id}/dossier", response_model=DossierSocietaire)
def dossier(
    societaire_id: str,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: ConsulterDossier = Depends(consulter_dossier),
    audit: JournalAuditSql = Depends(journal_audit),
) -> DossierSocietaire:
    resultat = cas_usage.executer(societaire_id)
    if resultat is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail={
                "code": "introuvable",
                "message": "Aucun sociétaire ne correspond à cet identifiant.",
            },
        )

    agence_agent = _agence_agent(utilisateur)
    if agence_agent is not None and resultat.identite.agence != agence_agent:
        raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")

    audit.enregistrer_evenement("consultation_dossier", str(utilisateur.id), societaire_id, {})
    return mappers.dossier_vers_schema(resultat)


@routeur.get("/{societaire_id}/groupe")
def groupe(
    societaire_id: str,
    utilisateur: Utilisateur = Depends(current_active_user),
    cas_usage: ConsulterDossier = Depends(consulter_dossier),
) -> dict[str, object]:
    resultat = cas_usage.executer(societaire_id)
    if resultat is None or resultat.identite.segment != "femme_gie" or resultat.groupe is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail={
                "code": "sans_groupe",
                "message": "Ce sociétaire n'appartient à aucun groupe actif.",
            },
        )

    agence_agent = _agence_agent(utilisateur)
    if agence_agent is not None and resultat.identite.agence != agence_agent:
        raise AccesRefuse("Ce sociétaire n'appartient pas à votre agence.")

    return mappers.groupe_vers_schema(resultat.groupe).model_dump()
