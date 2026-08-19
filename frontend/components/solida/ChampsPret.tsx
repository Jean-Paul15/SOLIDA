import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ProduitCreditApi } from "@/lib/contracts";
import { formaterMontant } from "@/lib/format";

interface ChampsPretProps {
  produits: ProduitCreditApi[];
  produit: ProduitCreditApi | undefined;
  produitId: string;
  onChangeProduit: (id: string) => void;
  montant: number;
  onChangeMontant: (montant: number) => void;
  duree: number;
  onChangeDuree: (duree: number) => void;
  dureePersonnalisee: boolean;
  dureesValides: number[];
  onChoisirDuree: (valeur: string) => void;
}

export function ChampsPret({
  produits,
  produit,
  produitId,
  onChangeProduit,
  montant,
  onChangeMontant,
  duree,
  onChangeDuree,
  dureePersonnalisee,
  dureesValides,
  onChoisirDuree,
}: ChampsPretProps) {
  return (
    <>
      <div className="flex flex-col gap-1.5">
        <Label>Produit de crédit</Label>
        <Select value={produitId} onValueChange={onChangeProduit}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {produits.map((p) => (
              <SelectItem key={p.produit_id} value={p.produit_id}>
                {p.libelle}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="montant">Montant sollicité</Label>
        <div className="flex items-center gap-2">
          <Input
            id="montant"
            type="number"
            value={montant}
            onChange={(e) => onChangeMontant(Number(e.target.value))}
            min={0}
            max={produit?.montant_max}
          />
          <span className="text-sm text-neutre-500">FCFA</span>
        </div>
        {produit && (
          <span className="text-xs text-neutre-500">
            Plafond du produit : {formaterMontant(produit.montant_max)}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <Label>Durée</Label>
        <Select value={dureePersonnalisee ? "autre" : String(duree)} onValueChange={onChoisirDuree}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {dureesValides.map((d) => (
              <SelectItem key={d} value={String(d)}>
                {d} mois
              </SelectItem>
            ))}
            <SelectItem value="autre">Autre (préciser)</SelectItem>
          </SelectContent>
        </Select>
        {produit && (
          <span className="text-xs text-neutre-500">
            Durée du produit : {produit.duree_min_mois}–{produit.duree_max_mois} mois
          </span>
        )}
        {dureePersonnalisee && (
          <div className="flex items-center gap-2">
            <Input
              type="number"
              min={produit?.duree_min_mois ?? 1}
              max={produit?.duree_max_mois ?? 60}
              value={duree}
              onChange={(e) => onChangeDuree(Number(e.target.value))}
              autoFocus
            />
            <span className="text-sm text-neutre-500">mois</span>
          </div>
        )}
      </div>
    </>
  );
}
