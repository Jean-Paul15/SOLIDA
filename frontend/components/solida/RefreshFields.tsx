import { ChevronRight } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ObjetCredit } from "@/lib/contracts";
import { LABEL_OBJET_CREDIT } from "@/lib/labels";

const OBJETS = Object.entries(LABEL_OBJET_CREDIT).map(([valeur, libelle]) => ({
  valeur: valeur as ObjetCredit,
  libelle,
}));

interface RefreshFieldsProps {
  objet: ObjetCredit;
  onChangeObjet: (objet: ObjetCredit) => void;
  refreshOpen: boolean;
  onToggleActualisation: () => void;
  revenu: number;
  onChangeRevenu: (revenu: number) => void;
  charges: number;
  onChangeCharges: (charges: number) => void;
}

export function RefreshFields({
  objet,
  onChangeObjet,
  refreshOpen,
  onToggleActualisation,
  revenu,
  onChangeRevenu,
  charges,
  onChangeCharges,
}: RefreshFieldsProps) {
  return (
    <>
      <div className="flex flex-col gap-1.5">
        <Label>Objet du crédit</Label>
        <Select value={objet} onValueChange={(v) => onChangeObjet(v as ObjetCredit)}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {OBJETS.map((o) => (
              <SelectItem key={o.valeur} value={o.valeur}>
                {o.libelle}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <button
        type="button"
        onClick={onToggleActualisation}
        className="flex cursor-pointer items-center gap-1 text-left text-sm text-neutre-700"
      >
        <ChevronRight
          className={
            refreshOpen ? "size-4 rotate-90 transition-transform" : "size-4 transition-transform"
          }
        />
        Actualiser la situation économique
      </button>

      {refreshOpen && (
        <div className="flex flex-col gap-3 border-l border-neutre-200 pl-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="revenu">Revenu mensuel</Label>
            <Input
              id="revenu"
              type="number"
              value={revenu}
              onChange={(e) => onChangeRevenu(Number(e.target.value))}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="charges">Charges mensuelles</Label>
            <Input
              id="charges"
              type="number"
              value={charges}
              onChange={(e) => onChangeCharges(Number(e.target.value))}
            />
          </div>
        </div>
      )}
    </>
  );
}
