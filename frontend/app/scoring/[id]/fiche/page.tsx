import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { EnTete } from "@/components/solida/EnTete";
import { FicheApercu } from "@/components/solida/FicheApercu";
import { FicheActions } from "@/components/solida/FicheActions";
import type { FicheJustification } from "@/lib/contracts";
import { lireDecision } from "@/lib/mocks/decisions";
import { societaires } from "@/lib/mocks/societaires";
import { lireSession } from "@/lib/session";

const VERSION_APPLICATION = "solida-frontend-0.1.0";

interface PageFicheProps {
  params: Promise<{ id: string }>;
}

export default async function PageFiche({ params }: PageFicheProps) {
  const { id: decisionId } = await params;
  const decision = lireDecision(decisionId);
  if (!decision) notFound();

  const { societaireId, demande, resultat } = decision;
  const fiche = societaires[societaireId];
  if (!fiche) notFound();

  const session = await lireSession();
  const favorables = resultat.decomposition.filter((c) => c.sens === "favorable").slice(0, 5);
  const defavorables = resultat.decomposition.filter((c) => c.sens === "defavorable").slice(0, 5);

  const ficheData: FicheJustification = {
    fiche_id: `fiche-${decisionId}`,
    resultat,
    demande,
    societaire_nom: fiche.dossier.identite.nom_complet,
    numero_membre: fiche.dossier.identite.numero_membre,
    agence: fiche.dossier.identite.agence,
    agent_nom: session?.nom ?? "Agent",
    date_edition: new Date().toISOString(),
    facteurs_favorables: favorables,
    facteurs_defavorables: defavorables,
    conditions_reexamen: resultat.conditions_reexamen,
    mention_legale:
      "Ce document présente les éléments ayant fondé la recommandation du système d'aide à la " +
      "décision. La décision finale relève de l'agent de crédit et du comité de crédit de la " +
      "coopérative.",
  };

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />
      <div className="mx-auto w-full max-w-[1000px] px-6 pt-4">
        <Link
          href={`/scoring/${decisionId}`}
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour au résultat
        </Link>
      </div>

      <main className="mx-auto flex w-full max-w-[1000px] flex-1 gap-6 px-6 py-6">
        <div className="flex-1">
          <FicheApercu fiche={ficheData} versionApplication={VERSION_APPLICATION} />
        </div>
        <FicheActions />
      </main>
    </div>
  );
}
