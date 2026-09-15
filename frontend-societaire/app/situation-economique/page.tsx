"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

// Facultatif : le sociétaire peut ne pas connaître ces montants précisément, ou ne pas
// vouloir les partager tout de suite — ce n'est jamais bloquant, contrairement au montant,
// à l'objet et à la durée (section 2, seule saisie libre autorisée hors montant et numéro
// de compte, au même titre). Sans ces informations, le modèle traite le revenu comme
// manquant (jamais comme zéro) : voir AVERTISSEMENT_REVENU_MANQUANT côté backend.
export default function SituationEconomiquePage() {
  const router = useRouter();
  const {
    jetonSession,
    dureeMois,
    revenuMensuelDeclare,
    chargesMensuelles,
    enregistrerSituationEconomique,
  } = useDemande();
  const [revenu, setRevenu] = React.useState(
    revenuMensuelDeclare ? String(revenuMensuelDeclare) : "",
  );
  const [charges, setCharges] = React.useState(
    chargesMensuelles ? String(chargesMensuelles) : "",
  );
  const pret = useEtapeProtegee(jetonSession);

  React.useEffect(() => {
    if (jetonSession && !dureeMois) router.replace("/duree");
  }, [jetonSession, dureeMois, router]);

  if (!pret || !dureeMois) return null;

  function continuer() {
    enregistrerSituationEconomique(
      revenu.length > 0 ? Number(revenu) : null,
      charges.length > 0 ? Number(charges) : null,
    );
    router.push("/recapitulatif");
  }

  return (
    <EcranEtape
      etape={7}
      titre="Pour mieux évaluer votre demande"
      sousTitre="Facultatif : ça aide votre agent, vous pouvez aussi passer cette étape."
      pied={<Button onClick={continuer}>Continuer</Button>}
    >
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="revenu-estime">Revenu mensuel estimé (FCFA)</Label>
          <NumericInput
            id="revenu-estime"
            value={revenu}
            onChange={(e) => setRevenu(e.target.value.replace(/\D/g, ""))}
            placeholder="Optionnel"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="charges-estimees">Charges mensuelles estimées (FCFA)</Label>
          <NumericInput
            id="charges-estimees"
            value={charges}
            onChange={(e) => setCharges(e.target.value.replace(/\D/g, ""))}
            placeholder="Optionnel"
          />
        </div>
      </div>
    </EcranEtape>
  );
}
