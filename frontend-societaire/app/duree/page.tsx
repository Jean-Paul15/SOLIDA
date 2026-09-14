"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChoixCarte } from "@/components/ui/choix-carte";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

// Catalogue "standard" : 3/6/9/12/18/24 mois, filtré aux bornes réelles du produit choisi
// (même logique que côté agent, frontend/components/solida/useNewRequest.ts). La durée
// reste toujours exprimée en mois : c'est la seule unité que le modèle et le catalogue
// produits connaissent (duree_min_mois/duree_max_mois) — pas de jours/semaines inventés.
const DUREES_STANDARD = [3, 6, 9, 12, 18, 24];
const AUTRE = "autre";

export default function DureePage() {
  const router = useRouter();
  const { jetonSession, produit, dureeMois, enregistrerDuree } = useDemande();
  const dureesValides = produit
    ? DUREES_STANDARD.filter(
        (d) => d >= produit.duree_min_mois && d <= produit.duree_max_mois,
      )
    : DUREES_STANDARD;
  const [selection, setSelection] = React.useState<
    number | typeof AUTRE | null
  >(
    dureeMois && dureesValides.includes(dureeMois)
      ? dureeMois
      : dureeMois
        ? AUTRE
        : null,
  );
  const [dureePersonnalisee, setDureePersonnalisee] = React.useState(
    dureeMois && !dureesValides.includes(dureeMois) ? String(dureeMois) : "",
  );
  const pret = useEtapeProtegee(jetonSession);
  React.useEffect(() => {
    if (jetonSession && !produit) router.replace("/produit");
  }, [jetonSession, produit, router]);

  if (!pret || !produit) return null;

  const bornesMin = produit.duree_min_mois;
  const bornesMax = produit.duree_max_mois;
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
    router.push("/recapitulatif");
  }

  return (
    <EcranEtape
      etape={7}
      titre="Sur combien de temps ?"
      pied={
        <Button onClick={continuer} disabled={!peutContinuer}>
          Continuer
        </Button>
      }
    >
      <div className="flex flex-col gap-2">
        {dureesValides.map((valeur) => (
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
            Durée en mois, entre {bornesMin} et {bornesMax} pour ce produit.
          </span>
        </div>
      )}
    </EcranEtape>
  );
}
