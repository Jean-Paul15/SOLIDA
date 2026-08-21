import type { ActiviteEconomique, IdentiteSocietaire } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";

const LIBELLE_NIVEAU_INSTRUCTION: Record<string, string> = {
  aucun: "Non renseigné",
  primaire: "Primaire",
  secondaire: "Secondaire",
  superieur: "Supérieur",
};

interface ProfilePanelProps {
  identite: IdentiteSocietaire;
  activite: ActiviteEconomique;
}

export function ProfilePanel({ identite, activite }: ProfilePanelProps) {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
      <span className="text-xs font-medium text-neutre-500">Profil</span>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <span className="text-neutre-500">Âge</span>
        <span className="text-neutre-950">{identite.age} ans</span>
        <span className="text-neutre-500">Personnes à charge</span>
        <span className="text-neutre-950">{activite.nb_personnes_a_charge}</span>
        <span className="text-neutre-500">Niveau d&rsquo;instruction</span>
        <span className="text-neutre-950">
          {LIBELLE_NIVEAU_INSTRUCTION[identite.niveau_instruction ?? "aucun"]}
        </span>
        <span className="text-neutre-500">Parts sociales</span>
        <span className="font-mono text-neutre-950">
          {formatAmount(activite.parts_sociales_montant)}
        </span>
      </div>
    </div>
  );
}
