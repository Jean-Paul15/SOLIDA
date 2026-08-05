import { leverSiEnErreur } from "@/lib/services/erreur-service";

export async function changerMotDePasse(
  motDePasseActuel: string,
  nouveauMotDePasse: string
): Promise<void> {
  const reponse = await fetch("/api/v1/auth/changer-mot-de-passe", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mot_de_passe_actuel: motDePasseActuel,
      nouveau_mot_de_passe: nouveauMotDePasse,
    }),
  });
  await leverSiEnErreur(reponse);
}
