import type { ObjetCredit } from "./objets-credit";

/**
 * Contrat d'API du portail sociétaire. Les endpoints ci-dessous ne sont PAS encore
 * implémentés côté backend (dette assumée et documentée, cf. le plan de ce chantier
 * et l'annexe sur l'état du schéma CORE-SIM v4) : ce fichier fixe la forme attendue
 * pour que l'intégration se limite, le moment venu, à écrire les endpoints et à
 * vérifier ce contrat — aucune autre pièce du portail n'a à changer.
 */

export interface VerificationCompteRequete {
  numero_compte: string;
  montant_dernier_depot: number;
}

export interface VerificationCompteReponse {
  jeton_session: string;
  prenom: string;
}

// 4 choix, pas une saisie libre (section 3 : "trois ou quatre choix seulement").
// Sous-ensemble des durées produites par le simulateur (3/6/9/12/18/24 mois) : les
// bornes courte et longue, plus deux intermédiaires usuelles.
export type DureeMois = 3 | 6 | 12 | 24;

export interface DemandePreVerificationRequete {
  montant: number;
  objet: ObjetCredit;
  duree_mois: DureeMois;
}

export type IssuePreVerification =
  | "peut_avancer"
  | "montant_reduit"
  | "duree_ou_attente"
  | "pas_maintenant";

export interface DemandePreVerificationReponse {
  issue: IssuePreVerification;
  message: string;
  /** Uniquement pour "montant_reduit" (objet divisible) : jamais présent avec un
   * objet indivisible, cf. règle section 1.7 / section 4 du parcours. */
  montant_propose?: number;
  demande_id: string;
}
