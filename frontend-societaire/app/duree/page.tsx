"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChoixCarte } from "@/components/ui/choix-carte";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

// Catalogue "standard" : 3/6/9/12/18/24 mois. La durée reste toujours exprimée en mois :
// c'est la seule unité que le modèle et le catalogue produits connaissent. Le produit
// n'est plus choisi à cette étape (déduit du segment du sociétaire à l'envoi de la
// demande) : DUREE_MIN/DUREE_MAX reprennent les bornes actuellement communes à tous les
// produits du catalogue (backend/solida CORE-SIM, table produits_credit -- vérifié le
// 15/09/2026, les cinq produits partagent 3-24 mois). Si un futur produit s'écarte de ces
// bornes, le serveur reste la seule source de vérité et refusera la demande hors bornes.
const DUREES_STANDARD = [3, 6, 9, 12, 18, 24];
const DUREE_MIN = 3;
const DUREE_MAX = 24;
const AUTRE = "autre";

export default function DureePage() {
  const router = useRouter();
  const { jetonSession, dureeMois, enregistrerDuree } = useDemande();
  const [selection, setSelection] = React.useState<
    number | typeof AUTRE | null
  >(
    dureeMois && DUREES_STANDARD.includes(dureeMois)
      ? dureeMois
      : dureeMois
        ? AUTRE
        : null,
  );
  const [dureePersonnalisee, setDureePersonnalisee] = React.useState(
    dureeMois && !DUREES_STANDARD.includes(dureeMois) ? String(dureeMois) : "",
  );
  const pret = useEtapeProtegee(jetonSession);

  if (!pret) return null;

  const bornesMin = DUREE_MIN;
  const bornesMax = DUREE_MAX;
  const personnalisee = Number(dureePersonnalisee);
  const personnaliseeValide =
    dureePersonnalisee.length > 0 &&
    personnalisee >= bornesMin &&
    personnalisee <= bornesMax;
  const peutContinuer =
    selection !== null && selection !== AUTRE
      ? true
      : selection === AUTRE && personnaliseeValide;

  function continuer() {
    if (!peutContinuer) return;
    enregistrerDuree(
      selection === AUTRE ? personnalisee : (selection as number),
    );
    router.push("/situation-economique");
  }

  return (
    <EcranEtape
      etape={6}
      titre="Sur combien de temps ?"
      pied={
        <Button onClick={continuer} disabled={!peutContinuer}>
          Continuer
        </Button>
      }
    >
      <div className="flex flex-col gap-2">
        {DUREES_STANDARD.map((valeur) => (
          <ChoixCarte
            key={valeur}
            libelle={`${valeur} mois`}
            selectionne={selection === valeur}
            onClick={() => setSelection(valeur)}
          />
        ))}
        <ChoixCarte
          libelle="Autre durée (préciser)"
          selectionne={selection === AUTRE}
          onClick={() => setSelection(AUTRE)}
        />
      </div>

      {selection === AUTRE && (
        <div className="mt-3 flex flex-col gap-1.5">
          <NumericInput
            value={dureePersonnalisee}
            onChange={(e) =>
              setDureePersonnalisee(e.target.value.replace(/\D/g, ""))
            }
            placeholder={`Entre ${bornesMin} et ${bornesMax}`}
            maxLength={4}
            autoFocus
          />
          <span className="text-center text-sm text-muted-foreground">
            Durée en mois, entre {bornesMin} et {bornesMax}.
          </span>
        </div>
      )}
    </EcranEtape>
  );
}
