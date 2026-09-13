import { apiFetch } from "./error-service";
import type {
  DemandePreVerificationReponse,
  DemandePreVerificationRequete,
  VerificationCompteReponse,
  VerificationCompteRequete,
} from "../contracts";

/**
 * Point d'appel unique vers le backend pour ce portail. Les deux endpoints appelés
 * ici (/api/v1/portail/...) ne sont pas encore construits côté backend — dette
 * documentée dans le plan de ce chantier. Le reste de l'app ne connaît que ces deux
 * fonctions : quand les endpoints existeront, seul ce fichier change.
 */

export async function verifierCompte(
  requete: VerificationCompteRequete
): Promise<VerificationCompteReponse> {
  const reponse = await apiFetch("/api/v1/portail/verification-compte", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requete),
  });
  return reponse.json();
}

export async function envoyerDemande(
  jetonSession: string,
  requete: DemandePreVerificationRequete
): Promise<DemandePreVerificationReponse> {
  const reponse = await apiFetch("/api/v1/portail/demandes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${jetonSession}`,
    },
    body: JSON.stringify(requete),
  });
  return reponse.json();
}
