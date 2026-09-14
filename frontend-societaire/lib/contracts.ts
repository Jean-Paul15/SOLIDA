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

/**
 * Durée en mois : seule unité que le catalogue produits (`duree_min_mois`/
 * `duree_max_mois`) et le modèle connaissent. Choix guidés (3/6/9/12/18/24 mois,
 * filtrés aux bornes du produit) avec une option "Autre durée" en saisie libre
 * bornée — déroge sciemment à SOLIDA_Flux_Societaire.md ("trois ou quatre choix
 * seulement, aucune saisie libre" pour cet écran), à la demande explicite du métier.
 */
export interface DemandePreVerificationRequete {
  montant: number;
  objet: ObjetCredit;
  duree_mois: number;
  produit_id: string;
}

/** Catalogue produits (même forme que côté agent, `frontend/lib/contracts.ts`) : le
 * sociétaire choisit un produit pour que l'agent l'ait sous les yeux, même si le
 * modèle ne le consomme pas directement comme feature. */
export interface ProduitCreditApi {
  produit_id: string;
  libelle: string;
  type_garantie: string;
  montant_min: number;
  montant_max: number;
  duree_min_mois: number;
  duree_max_mois: number;
  taux_annuel: number;
}

export type IssuePreVerification =
  "peut_avancer" | "montant_reduit" | "duree_ou_attente" | "pas_maintenant";

export interface DemandePreVerificationReponse {
  issue: IssuePreVerification;
  message: string;
  /** Uniquement pour "montant_reduit" (objet divisible) : jamais présent avec un
   * objet indivisible, cf. règle section 1.7 / section 4 du parcours. */
  montant_propose?: number;
  demande_id: string;
}
