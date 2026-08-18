"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { ResultatScoringVue } from "@/components/solida/ResultatScoringVue";
import { ApiError } from "@/lib/services/error-service";
import { confirmDecision } from "@/lib/services/scoring";
import { usePreview } from "@/lib/preview-context";

export default function PagePrevisualisationScoring() {
  const router = useRouter();
  const { previsualisation, definirPrevisualisation } = usePreview();
  const [confirmationEnCours, setConfirmationEnCours] = useState(false);

  if (!previsualisation) {
    return (
      <div className="mx-auto flex min-h-screen max-w-[600px] flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="text-sm text-neutre-500">
          Aucun aperçu de score en attente. Repartez de la recherche pour lancer une nouvelle
          demande.
        </p>
        <Link href="/" className="text-sm text-solida-teal-800 underline">
          Retour à la recherche
        </Link>
      </div>
    );
  }

  const { entree, resultat, societaireNom } = previsualisation;

  async function surConfirmer() {
    setConfirmationEnCours(true);
    try {
      const enregistre = await confirmDecision(entree);
      toast.success("Décision enregistrée.");
      definirPrevisualisation(null);
      router.push(`/scoring/${enregistre.decision_id}`);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "L'enregistrement a échoué.");
      setConfirmationEnCours(false);
    }
  }

  function surAnnuler() {
    definirPrevisualisation(null);
    router.push(`/societaires/${entree.societaire_id}`);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
        <Link
          href={`/societaires/${entree.societaire_id}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au dossier de {societaireNom}
        </Link>
      </div>
      <main className="flex flex-1 flex-col">
        <ResultatScoringVue
          resultat={resultat}
          previsualisation
          surConfirmer={surConfirmer}
          surAnnuler={surAnnuler}
          confirmationEnCours={confirmationEnCours}
        />
      </main>
    </div>
  );
}
