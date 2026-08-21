import { GroupeCautionDialog } from "@/components/solida/GroupeCautionDialog";
import type { SyntheseEpargne, SyntheseGroupe } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";

interface GuaranteePanelProps {
  segment: string;
  groupe: SyntheseGroupe | undefined;
  societaireId: string;
  epargne: SyntheseEpargne;
}

export function GuaranteePanel({ segment, groupe, societaireId, epargne }: GuaranteePanelProps) {
  if (segment === "femme_gie" && groupe) {
    return (
      <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
        <span className="text-xs font-medium text-neutre-500">Groupe de caution</span>
        <span className="text-sm font-medium text-neutre-950">{groupe.nom_groupe}</span>
        {groupe.taux_remboursement_groupe !== null ? (
          <span className="font-mono text-lg text-neutre-950">
            {Math.round(groupe.taux_remboursement_groupe * 100)}%
          </span>
        ) : (
          <span className="text-sm text-neutre-500">
            Le groupe ne dispose pas encore d&rsquo;un historique de remboursement suffisant. Le
            scoring s&rsquo;appuiera sur le profil individuel.
          </span>
        )}
        <GroupeCautionDialog societaireId={societaireId} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
      <span className="text-xs font-medium text-neutre-500">Épargne disponible</span>
      <span className="font-mono text-lg text-neutre-950">
        {formatAmount(epargne.solde_moyen_6m)}
      </span>
      <span className="text-xs text-neutre-500">Garantie de droit commun sur ce dossier.</span>
    </div>
  );
}
