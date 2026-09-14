"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChoixCarte } from "@/components/ui/choix-carte";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { fetchProduits } from "@/lib/services/portail";
import { afficherErreur } from "@/lib/services/error-service";
import type { ProduitCreditApi } from "@/lib/contracts";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

export default function ProduitPage() {
  const router = useRouter();
  const { jetonSession, produit, enregistrerProduit } = useDemande();
  const [produits, setProduits] = React.useState<ProduitCreditApi[] | null>(
    null,
  );
  const [selection, setSelection] = React.useState<string | null>(
    produit?.produit_id ?? null,
  );
  const pret = useEtapeProtegee(jetonSession);

  React.useEffect(() => {
    if (!jetonSession) return;
    fetchProduits(jetonSession)
      .then(setProduits)
      .catch((erreur) =>
        afficherErreur(erreur, "Impossible de charger les produits."),
      );
  }, [jetonSession]);

  if (!pret) return null;

  function continuer() {
    const choisi = produits?.find((p) => p.produit_id === selection);
    if (!choisi) return;
    enregistrerProduit(choisi);
    router.push("/duree");
  }

  return (
    <EcranEtape
      etape={6}
      titre="Pour quel produit ?"
      pied={
        <Button onClick={continuer} disabled={!selection}>
          Continuer
        </Button>
      }
    >
      {produits === null ? (
        <div className="animate-shimmer flex flex-col gap-2">
          <div className="h-12 rounded-lg bg-neutre-100" />
          <div className="h-12 rounded-lg bg-neutre-100" />
          <div className="h-12 rounded-lg bg-neutre-100" />
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {produits.map((p) => (
            <ChoixCarte
              key={p.produit_id}
              libelle={p.libelle}
              selectionne={selection === p.produit_id}
              onClick={() => setSelection(p.produit_id)}
            />
          ))}
        </div>
      )}
    </EcranEtape>
  );
}
