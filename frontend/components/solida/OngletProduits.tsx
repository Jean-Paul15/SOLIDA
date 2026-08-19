import { Input } from "@/components/ui/input";
import { Rubrique } from "@/components/solida/Rubrique";
import type { ProduitCreditApi } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";

interface OngletProduitsProps {
  produits: ProduitCreditApi[];
  plafondsProduits: Record<string, number>;
  onChangePlafond: (produitId: string, valeur: number) => void;
  autoriseAModifier: boolean;
  version: string;
}

export function OngletProduits({
  produits,
  plafondsProduits,
  onChangePlafond,
  autoriseAModifier,
  version,
}: OngletProduitsProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <Rubrique
          titre="Plafonds par produit"
          description="Indépendant des curseurs de l'onglet Seuils : plafond maximal appliqué quel que soit le score."
        />
        <span className="text-xs text-neutre-500">Version active : {version}</span>
      </div>
      <div className="flex flex-col gap-3 rounded-lg border border-neutre-200 p-4">
        {produits.map((p) => (
          <div key={p.produit_id} className="flex items-center gap-3 text-sm">
            <div className="flex flex-1 flex-col">
              <span className="text-neutre-950">{p.libelle}</span>
              <span className="text-xs text-neutre-500">
                {p.duree_min_mois}–{p.duree_max_mois} mois · {(p.taux_annuel * 100).toFixed(0)}% ·{" "}
                {p.type_garantie}
              </span>
            </div>
            {autoriseAModifier ? (
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  className="w-32"
                  value={plafondsProduits[p.produit_id] ?? p.montant_max}
                  onChange={(e) => onChangePlafond(p.produit_id, Number(e.target.value))}
                  min={p.montant_min}
                />
                <span className="text-xs text-neutre-500">FCFA</span>
              </div>
            ) : (
              <span className="font-mono text-neutre-950">
                {formaterMontant(plafondsProduits[p.produit_id] ?? p.montant_max)}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
