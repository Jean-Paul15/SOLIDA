"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { NumericInput } from "@/components/ui/numeric-input";
import { EcranEtape } from "@/components/parcours/ecran-etape";
import { useDemande } from "@/lib/demande-context";
import { formaterFcfa } from "@/lib/format";
import { useEtapeProtegee } from "@/lib/use-etape-protegee";

// Saisie libre du montant (section 3 de SOLIDA_Flux_Societaire.md : "aucune saisie libre en
// dehors du numéro de compte et du montant" -- le montant est l'une des deux exceptions
// documentées). Aucun plancher ni plafond affiché ou imposé côté client au-delà de "non nul" :
// le serveur applique toujours la grille active, seule source de vérité. MONTANT_SEUIL_ALERTE
// reprend le plafond institutionnel par défaut (backend/solida/domain/rules/grille.py,
// "plafond_institutionnel_fcfa") uniquement pour avertir d'une saisie inhabituelle, jamais pour
// bloquer la saisie.
const MONTANT_SEUIL_ALERTE = 100_000_000;

export default function MontantPage() {
  const router = useRouter();
  const { jetonSession, montant: montantExistant, enregistrerMontant } = useDemande();
  const [montantSaisi, setMontantSaisi] = React.useState(
    montantExistant ? String(montantExistant) : ""
  );
  const pret = useEtapeProtegee(jetonSession);

  if (!pret) return null;

  const montant = Number(montantSaisi);
  const valide = montantSaisi.length > 0 && montant > 0;
  const montantInhabituel = valide && montant >= MONTANT_SEUIL_ALERTE;

  function continuer() {
    if (!valide) return;
    enregistrerMontant(montant);
    router.push("/objet");
  }

  return (
    <EcranEtape
      etape={4}
      titre="Combien souhaitez-vous ?"
      pied={
        <Button onClick={continuer} disabled={!valide}>
          Continuer
        </Button>
      }
    >
      <div className="flex flex-col gap-1.5">
        <NumericInput
          value={montantSaisi}
          onChange={(e) => setMontantSaisi(e.target.value.replace(/\D/g, ""))}
          placeholder="Montant en FCFA"
          maxLength={9}
          autoFocus
          aria-label="Montant souhaité"
        />
        {montantInhabituel && (
          <span className="text-center text-sm text-amber-600" role="alert">
            Montant inhabituel ({formaterFcfa(montant)}) : vérifiez votre saisie avant de
            continuer.
          </span>
        )}
      </div>
    </EcranEtape>
  );
}
