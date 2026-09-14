"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ScoringResultView } from "@/components/solida/ScoringResultView";
import { useApiErrorToast } from "@/lib/services/error-service";
import { confirmDecision } from "@/lib/services/scoring";
import { usePreview } from "@/lib/preview-context";
import { withMinDuration } from "@/lib/timing";
import { ECHEC, useAsyncAction } from "@/lib/use-async-action";

export default function PagePrevisualisationScoring() {
  const router = useRouter();
  const { preview, setPreview } = usePreview();
  const { inProgress: confirmationInProgress, run } = useAsyncAction();
  const handleError = useApiErrorToast();

  if (!preview) {
    return (
      <div className="mx-auto flex flex-1 max-w-[600px] flex-col items-center justify-center gap-4 px-6 text-center">
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
    const enregistre = await run(() => withMinDuration(confirmDecision(input)), {
      fallbackErrorMessage: "L'enregistrement a échoué.",
      onError: (e) => handleError(e, "L'enregistrement a échoué."),
    });
    if (enregistre !== ECHEC) {
      toast.success("Décision enregistrée.");
      setPreview(null);
      router.push(`/scoring/${enregistre.decision_id}`);
    }
  }

  function handleCancel() {
    setPreview(null);
    router.push(`/societaires/${input.societaire_id}`);
  }

  return (
    <>
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
    </>
  );
}
