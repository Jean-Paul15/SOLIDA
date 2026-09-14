"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";

// Plage et repères : plafond du catalogue produits documenté
// (PLAN 72H/SOLIDA_Complements_et_Strategie.md, PLAN 72H/SOLIDA_Schema_Donnees_a_valider.md
// section 9.2 : "plafond 3 000 000"). Le simulateur tire des montants jusqu'à 5,5M pour
// varier le jeu d'entraînement, mais ce n'est pas le plafond produit réel présenté au
// sociétaire — à confirmer si un praticien valide un autre plafond.
const MONTANT_MIN = 50_000;
const MONTANT_MAX = 3_000_000;
const PAS = 10_000;
const REPERES = [50_000, 500_000, 1_500_000, 3_000_000];

function formaterFcfa(valeur: number): string {
  return `${new Intl.NumberFormat("fr-FR").format(valeur)} FCFA`;
}

export default function MontantPage() {
  const router = useRouter();
  const { jetonSession, enregistrerMontant } = useDemande();
  const [montant, setMontant] = React.useState(200_000);

  React.useEffect(() => {
    if (!jetonSession) router.replace("/numero-compte");
  }, [jetonSession, router]);

  if (!jetonSession) return null;

  function continuer() {
    enregistrerMontant(montant);
    router.push("/objet");
  }

  return (
    <EcranEtape
      etape={4}
      titre="Combien souhaitez-vous ?"
      pied={<Button onClick={continuer}>Continuer</Button>}
    >
      <p className="text-center font-mono text-2xl font-semibold text-solida-teal-800">
        {formaterFcfa(montant)}
      </p>

      <div className="mt-8">
        <Slider
          value={[montant]}
          onValueChange={([valeur]) => setMontant(valeur)}
          min={MONTANT_MIN}
          max={MONTANT_MAX}
          step={PAS}
          aria-label="Montant souhaité"
        />
        <div className="mt-2 flex justify-between text-sm text-muted-foreground">
          {REPERES.map((repere) => (
            <span key={repere}>{new Intl.NumberFormat("fr-FR").format(repere)}</span>
          ))}
        </div>
      </div>
    </EcranEtape>
  );
}
