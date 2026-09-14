"use client";

import { useRouter } from "next/navigation";
import { CircleCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

export default function BonjourPage() {
  const router = useRouter();
  const { prenom, jetonSession } = useDemande();
  const pret = useEtapeProtegee(jetonSession);

  if (!pret) return null;

  return (
    <EcranEtape
      etape={3}
      titre={`Bonjour ${prenom}`}
      sousTitre="Nous vous avons bien reconnu. Voyons ensemble votre demande."
      pied={<Button onClick={() => router.push("/montant")}>Continuer</Button>}
    >
      <div className="flex justify-center py-3">
        <CircleCheck className="size-12 text-succes" strokeWidth={1.5} />
      </div>
    </EcranEtape>
  );
}
