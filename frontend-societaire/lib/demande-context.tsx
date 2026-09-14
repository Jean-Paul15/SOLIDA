"use client";

import * as React from "react";
import type {
  DemandePreVerificationReponse,
  ProduitCreditApi,
} from "./contracts";
import type { ObjetCredit } from "./objets-credit";

/**
 * État du parcours, en mémoire uniquement (React state, jamais localStorage/
 * sessionStorage — cf. lib/offline-queue.ts pour l'unique exception documentée).
 * Perdu à un rechargement complet de page : voulu, ça matérialise la "session
 * courte" exigée section 2 du document sans avoir à gérer d'expiration explicite.
 */
interface EtatDemande {
  numeroCompte: string | null;
  jetonSession: string | null;
  prenom: string | null;
  montant: number | null;
  objet: ObjetCredit | null;
  produit: ProduitCreditApi | null;
  dureeMois: number | null;
  resultat: DemandePreVerificationReponse | null;
}

const ETAT_INITIAL: EtatDemande = {
  numeroCompte: null,
  jetonSession: null,
  prenom: null,
  montant: null,
  objet: null,
  produit: null,
  dureeMois: null,
  resultat: null,
};

interface ContexteDemande extends EtatDemande {
  enregistrerNumeroCompte: (numeroCompte: string) => void;
  enregistrerVerification: (jetonSession: string, prenom: string) => void;
  enregistrerMontant: (montant: number) => void;
  enregistrerObjet: (objet: ObjetCredit) => void;
  enregistrerProduit: (produit: ProduitCreditApi) => void;
  enregistrerDuree: (dureeMois: number) => void;
  enregistrerResultat: (resultat: DemandePreVerificationReponse) => void;
  reinitialiser: () => void;
}

const Contexte = React.createContext<ContexteDemande | null>(null);

export function DemandeProvider({ children }: { children: React.ReactNode }) {
  const [etat, setEtat] = React.useState<EtatDemande>(ETAT_INITIAL);

  const valeur = React.useMemo<ContexteDemande>(
    () => ({
      ...etat,
      enregistrerNumeroCompte: (numeroCompte) =>
        setEtat((precedent) => ({ ...precedent, numeroCompte })),
      enregistrerVerification: (jetonSession, prenom) =>
        setEtat((precedent) => ({ ...precedent, jetonSession, prenom })),
      // Changer une réponse en amont invalide la pré-vérification déjà obtenue :
      // sans ça, un retour en arrière pour corriger l'objet ou la durée laisserait
      // affiché un message calculé pour une demande différente (repéré en testant
      // le parcours dans le navigateur).
      enregistrerMontant: (montant) =>
        setEtat((precedent) => ({ ...precedent, montant, resultat: null })),
      enregistrerObjet: (objet) =>
        setEtat((precedent) => ({ ...precedent, objet, resultat: null })),
      enregistrerProduit: (produit) =>
        setEtat((precedent) => ({ ...precedent, produit, resultat: null })),
      enregistrerDuree: (dureeMois) =>
        setEtat((precedent) => ({ ...precedent, dureeMois, resultat: null })),
      enregistrerResultat: (resultat) =>
        setEtat((precedent) => ({ ...precedent, resultat })),
      reinitialiser: () => setEtat(ETAT_INITIAL),
    }),
    [etat],
  );

  return <Contexte.Provider value={valeur}>{children}</Contexte.Provider>;
}

export function useDemande(): ContexteDemande {
  const contexte = React.useContext(Contexte);
  if (!contexte) {
    throw new Error("useDemande doit être utilisé sous DemandeProvider");
  }
  return contexte;
}
