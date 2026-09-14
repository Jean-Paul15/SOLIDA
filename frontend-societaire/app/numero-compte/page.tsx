"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";

export default function NumeroComptePage() {
  const router = useRouter();
  const { enregistrerNumeroCompte } = useDemande();
  const [numero, setNumero] = React.useState("");

  const valide = numero.length >= 4;

  function continuer() {
    if (!valide) return;
    enregistrerNumeroCompte(numero);
    router.push("/verification");
  }

  return (
    <EcranEtape
      etape={1}
      titre="Quel est votre numéro de compte ?"
      sousTitre="Celui qui figure sur votre livret."
      precedent="/"
      pied={
        <Button onClick={continuer} disabled={!valide}>
          Continuer
        </Button>
      }
    >
      <Label htmlFor="numero-compte">Numéro de compte</Label>
      <NumericInput
        id="numero-compte"
        value={numero}
        onChange={(event) => setNumero(event.target.value.replace(/\D/g, ""))}
        placeholder="••••••"
        maxLength={12}
        autoFocus
      />
    </EcranEtape>
  );
}
