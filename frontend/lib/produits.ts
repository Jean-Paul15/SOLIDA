import type { ProduitCreditApi } from "@/lib/contracts";

/**
 * Catalogue de produits réel, servi par `GET /api/v1/produits` (référentiel CORE-SIM fusionné
 * avec le plafond ajustable de la grille active) — plus de tableau statique en dur.
 */
export function findProduit(
  produits: ProduitCreditApi[],
  produitId: string
): ProduitCreditApi | undefined {
  return produits.find((p) => p.produit_id === produitId);
}
