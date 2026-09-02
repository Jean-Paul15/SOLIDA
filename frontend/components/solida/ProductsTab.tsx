import { Input } from "@/components/ui/input";
import { Section } from "@/components/solida/Section";
import type { ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";

interface ProductsTabProps {
  products: ProduitCreditApi[];
  productCaps: Record<string, number>;
  onProductCapChange: (produitId: string, value: number) => void;
  canEdit: boolean;
  version: string;
}

export function ProductsTab({
  products,
  productCaps,
  onProductCapChange,
  canEdit,
  version,
}: ProductsTabProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <Section
          title="Plafonds par produit"
          description="Indépendant des curseurs de l'onglet Seuils : plafond maximal appliqué quel que soit le score."
        />
        <span className="text-xs text-neutre-500">Version active : {version}</span>
      </div>
      <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
        {products.map((product) => (
          <div key={product.produit_id} className="flex items-center gap-3 text-sm">
            <div className="flex flex-1 flex-col">
              <span className="text-neutre-950">{product.libelle}</span>
              <span className="text-xs text-neutre-500">
                {product.duree_min_mois}–{product.duree_max_mois} mois ·{" "}
                {(product.taux_annuel * 100).toFixed(0)}% · {product.type_garantie}
              </span>
            </div>
            {canEdit ? (
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  className="w-32"
                  value={productCaps[product.produit_id] ?? product.montant_max}
                  onChange={(event) =>
                    onProductCapChange(product.produit_id, Number(event.target.value))
                  }
                  min={product.montant_min}
                />
                <span className="text-xs text-neutre-500">FCFA</span>
              </div>
            ) : (
              <span className="font-mono text-neutre-950">
                {formatAmount(productCaps[product.produit_id] ?? product.montant_max)}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
