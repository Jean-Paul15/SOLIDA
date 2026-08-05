import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { EnTete } from "@/components/solida/EnTete";
import { ResultatScoringVue } from "@/components/solida/ResultatScoringVue";
import { fetchBackend } from "@/lib/backend";
import type { DossierSocietaire, ResultatScoring } from "@/lib/contracts";
import { exigerMotDePasseAJour, lireSession } from "@/lib/session";

interface PageResultatScoringProps {
  params: Promise<{ id: string }>;
}

export default async function PageResultatScoring({ params }: PageResultatScoringProps) {
  const { id: decisionId } = await params;
  const reponse = await fetchBackend(`/api/v1/scoring/${decisionId}`);
  if (!reponse.ok) notFound();
  const resultat: ResultatScoring = await reponse.json();

  const reponseDossier = await fetchBackend(
    `/api/v1/societaires/${resultat.societaire_id}/dossier`
  );
  if (!reponseDossier.ok) notFound();
  const dossier: DossierSocietaire = await reponseDossier.json();

  const session = await lireSession();
  exigerMotDePasseAJour(session);

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />
      <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
        <Link
          href={`/societaires/${resultat.societaire_id}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au dossier de {dossier.identite.nom_complet}
        </Link>
      </div>
      <main className="flex flex-1 flex-col">
        <ResultatScoringVue resultat={resultat} />
      </main>
    </div>
  );
}
