export interface ProduitCredit {
  id: string;
  nom: string;
  plafond: number;
}

/**
 * Catalogue de produits, en dur côté frontend en attendant un vrai catalogue
 * backend. `plafond` est un plafond de produit (décidé par la coopérative),
 * pas une sortie du modèle — voir `domain.rules.progressif.ParametresProgressif.plafond_produit`
 * côté backend pour l'équivalent qui doit un jour piloter cette valeur.
 */
export const PRODUITS: ProduitCredit[] = [
  { id: "prod-commerce", nom: "Crédit commerce", plafond: 2_000_000 },
  { id: "prod-agricole", nom: "Crédit agricole", plafond: 1_500_000 },
  { id: "prod-equipement", nom: "Crédit équipement", plafond: 3_000_000 },
];

export function trouverProduit(produitId: string): ProduitCredit {
  return PRODUITS.find((p) => p.id === produitId) ?? PRODUITS[0];
}
