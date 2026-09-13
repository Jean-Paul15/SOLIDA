"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { CircleCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";

export default function BonjourPage() {
  const router = useRouter();
  const { prenom, jetonSession } = useDemande();

  React.useEffect(() => {
    if (!jetonSession) router.replace("/numero-compte");
  }, [jetonSession, router]);

  if (!jetonSession) return null;

  return (
    <EcranEtape
      etape={3}
      titre={`Bonjour ${prenom}`}
      sousTitre="Nous vous avons bien reconnu. Voyons ensemble votre demande."
      pied={<Button onClick={() => router.push("/montant")}>Continuer</Button>}
    >
      <div className="flex justify-center py-6">
        <CircleCheck className="size-16 text-succes" strokeWidth={1.5} />
      </div>
    </EcranEtape>
  );
}
