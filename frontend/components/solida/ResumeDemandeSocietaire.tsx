import type { DemandeSocietaireApi, ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { LABEL_OBJET_CREDIT } from "@/lib/labels";
import { findProduit } from "@/lib/produits";

interface ResumeDemandeSocietaireProps {
  demande: DemandeSocietaireApi;
  produits: ProduitCreditApi[];
}

/** Ce que le sociétaire a réellement rempli sur le portail — distinct de la recommandation
 * du modèle (`ScoringResultView`, affiché juste en dessous) : sans ce résumé, l'agent perd
 * de vue le produit et la durée choisis dès qu'il ouvre le détail d'une notification, alors
 * que la liste elle-même ne montre que l'objet. */
export function ResumeDemandeSocietaire({ demande, produits }: ResumeDemandeSocietaireProps) {
  const produit = findProduit(produits, demande.produit_id);

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-3 rounded-lg border border-neutre-200 bg-neutre-50 p-4 text-sm sm:grid-cols-4">
      <div>
        <span className="text-neutre-500">Produit</span>
        <div className="font-medium text-neutre-950">{produit?.libelle ?? demande.produit_id}</div>
      </div>
      <div>
        <span className="text-neutre-500">Objet</span>
        <div className="font-medium text-neutre-950">
          {LABEL_OBJET_CREDIT[demande.objet_credit]}
        </div>
      </div>
      <div>
        <span className="text-neutre-500">Durée demandée</span>
        <div className="font-medium text-neutre-950">{demande.duree_mois} mois</div>
      </div>
      <div>
        <span className="text-neutre-500">Montant demandé</span>
        <div className="font-mono font-medium text-neutre-950">
          {formatAmount(demande.montant_demande)}
        </div>
      </div>
    </div>
  );
}
