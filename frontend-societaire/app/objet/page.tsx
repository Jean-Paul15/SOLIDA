"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChoixCarte } from "@/components/ui/choix-carte";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import {
  LISTE_OBJETS_CREDIT,
  OBJETS_CREDIT,
  type ObjetCredit,
} from "@/lib/objets-credit";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

export default function ObjetPage() {
  const router = useRouter();
  const { jetonSession, objet, enregistrerObjet } = useDemande();
  const [selection, setSelection] = React.useState<ObjetCredit | null>(objet);
  const pret = useEtapeProtegee(jetonSession);

  if (!pret) return null;

  function continuer() {
    if (!selection) return;
    enregistrerObjet(selection);
    router.push("/duree");
  }

  return (
    <EcranEtape
      etape={5}
      titre="Pour quoi faire ?"
      pied={
        <Button onClick={continuer} disabled={!selection}>
          Continuer
        </Button>
      }
    >
      <div className="grid grid-cols-2 gap-2.5">
        {LISTE_OBJETS_CREDIT.map((cle) => {
          const { libelle, icone } = OBJETS_CREDIT[cle];
          return (
            <ChoixCarte
              key={cle}
              disposition="grille"
              libelle={libelle}
              icone={icone}
              selectionne={selection === cle}
              onClick={() => setSelection(cle)}
            />
          );
        })}
      </div>
    </EcranEtape>
  );
}
