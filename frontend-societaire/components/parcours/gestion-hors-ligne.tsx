"use client";

import * as React from "react";
import { toast } from "sonner";
import { envoyerDemande } from "@/lib/services/portail";
import { lireFile, viderFile } from "@/lib/offline-queue";

/**
 * Monté une fois dans le layout racine : tente d'envoyer la demande en file dès que
 * le réseau revient (événement `online`), et au montage de l'app (cas d'une demande
 * restée en file après fermeture du navigateur). Section 6 : "part dès le retour du
 * réseau", sans action de l'utilisateur.
 */
export function GestionHorsLigne() {
  React.useEffect(() => {
    let actif = true;

    async function tenterEnvoi() {
      const enAttente = await lireFile().catch(() => undefined);
      if (!enAttente || !actif) return;
      try {
        await envoyerDemande(enAttente.jeton_session, {
          montant: enAttente.montant,
          objet: enAttente.objet as never,
          duree_mois: enAttente.duree_mois as never,
        });
        await viderFile();
        if (actif) toast.success("Votre demande, gardée en attente, vient d'être envoyée à votre agent.");
      } catch {
        // Réseau toujours indisponible ou session expirée : on retente au prochain
        // événement "online", rien à signaler à l'utilisateur (déjà informé à C8).
      }
    }

    tenterEnvoi();
    window.addEventListener("online", tenterEnvoi);
    return () => {
      actif = false;
      window.removeEventListener("online", tenterEnvoi);
    };
  }, []);

  return null;
}
