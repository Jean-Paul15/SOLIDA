import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ScoringResultView } from "@/components/solida/ScoringResultView";
import { fetchBackend } from "@/lib/backend";
import type { DossierSocietaire, ScoringResult } from "@/lib/contracts";
import { redirectIfAccessDenied, redirectIfUnauthenticated } from "@/lib/session";

interface PageResultatScoringProps {
  params: Promise<{ id: string }>;
}

export default async function PageResultatScoring({ params }: PageResultatScoringProps) {
  const { id: decisionId } = await params;
  const reponse = await fetchBackend(`/api/v1/scoring/${decisionId}`);
  redirectIfUnauthenticated(reponse);
  redirectIfAccessDenied(reponse);
  if (!reponse.ok) notFound();
  const result: ScoringResult = await reponse.json();

  const reponseDossier = await fetchBackend(`/api/v1/societaires/${result.societaire_id}/dossier`);
  redirectIfUnauthenticated(reponseDossier);
  redirectIfAccessDenied(reponseDossier);
  if (!reponseDossier.ok) notFound();
  const dossier: DossierSocietaire = await reponseDossier.json();

  return (
    <>
      <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
        <Link
          href={`/societaires/${result.societaire_id}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au dossier de {dossier.identite.nom_complet}
        </Link>
      </div>
      <main className="flex flex-1 flex-col">
        <ScoringResultView result={result} />
      </main>
    </>
  );
}
