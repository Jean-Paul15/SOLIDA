import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { EnTete } from "@/components/solida/EnTete";
import { ResultatScoringVue } from "@/components/solida/ResultatScoringVue";
import { lireDecision } from "@/lib/mocks/decisions";
import { societaires } from "@/lib/mocks/societaires";
import { lireSession } from "@/lib/session";

interface PageResultatScoringProps {
  params: Promise<{ id: string }>;
}

export default async function PageResultatScoring({ params }: PageResultatScoringProps) {
  const { id: decisionId } = await params;
  const decision = lireDecision(decisionId);
  if (!decision) notFound();

  const { societaireId, resultat } = decision;
  const fiche = societaires[societaireId];
  if (!fiche) notFound();

  const session = await lireSession();

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />
      <div className="mx-auto w-full max-w-[1440px] px-6 pt-4">
        <Link
          href={`/societaires/${societaireId}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au dossier de {fiche.dossier.identite.nom_complet}
        </Link>
      </div>
      <ResultatScoringVue resultat={resultat} />
    </div>
  );
}
