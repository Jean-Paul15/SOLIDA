import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Header } from "@/components/solida/Header";
import type { DecisionRegistreVue } from "@/components/solida/RegistreDecisions";
import { RegistreDecisions } from "@/components/solida/RegistreDecisions";
import { fetchBackend } from "@/lib/backend";
import type { DecisionRegistreApi } from "@/lib/contracts";
import { enforcePasswordUpToDate, readSession, redirectIfUnauthenticated } from "@/lib/session";

export default async function PageRegistre() {
  const session = await readSession();
  enforcePasswordUpToDate(session);

  const reponse = await fetchBackend("/api/v1/registre?limite=50");
  redirectIfUnauthenticated(reponse);
  const { elements }: { elements: DecisionRegistreApi[]; total: number } = reponse.ok
    ? await reponse.json()
    : { elements: [], total: 0 };

  const decisions: DecisionRegistreVue[] = elements.map((d) => ({
    decisionId: d.decision_id,
    societaireId: d.societaire_id,
    societaireNom: d.societaire_nom,
    agence: d.agence,
    result: d.resultat,
    timestamp: d.horodatage,
    agentName: d.agent_nom,
  }));

  return (
    <div className="flex min-h-screen flex-col">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />
      <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-4 px-6 py-6">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour à la recherche
        </Link>
        <h1 className="font-serif-title text-lg font-semibold text-neutre-950">
          Registre des décisions
        </h1>
        <RegistreDecisions decisions={decisions} />
      </main>
    </div>
  );
}
