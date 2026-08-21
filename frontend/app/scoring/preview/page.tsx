"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { ScoringResultView } from "@/components/solida/ScoringResultView";
import { ApiError } from "@/lib/services/error-service";
import { confirmDecision } from "@/lib/services/scoring";
import { usePreview } from "@/lib/preview-context";

export default function PagePrevisualisationScoring() {
  const router = useRouter();
  const { preview, setPreview } = usePreview();
  const [confirmationInProgress, setConfirmationInProgress] = useState(false);

  if (!preview) {
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

  const { input, result, societaireNom } = preview;

  async function handleConfirm() {
    setConfirmationInProgress(true);
    try {
      const enregistre = await confirmDecision(input);
      toast.success("Décision enregistrée.");
      setPreview(null);
      router.push(`/scoring/${enregistre.decision_id}`);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "L'enregistrement a échoué.");
      setConfirmationInProgress(false);
    }
  }

  function handleCancel() {
    setPreview(null);
    router.push(`/societaires/${input.societaire_id}`);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
        <Link
          href={`/societaires/${input.societaire_id}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au dossier de {societaireNom}
        </Link>
      </div>
      <main className="flex flex-1 flex-col">
        <ScoringResultView
          result={result}
          isPreview
          onConfirm={handleConfirm}
          onCancel={handleCancel}
          confirmationInProgress={confirmationInProgress}
        />
      </main>
    </div>
  );
}
