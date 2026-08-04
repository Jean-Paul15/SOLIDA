import { EnTete } from "@/components/solida/EnTete";
import type { DecisionRegistreVue } from "@/components/solida/RegistreDecisions";
import { RegistreDecisions } from "@/components/solida/RegistreDecisions";
import { fetchBackend } from "@/lib/backend";
import type { DecisionRegistreApi } from "@/lib/contracts";
import { lireSession } from "@/lib/session";

export default async function PageRegistre() {
  const session = await lireSession();

  const reponse = await fetchBackend("/api/v1/registre?limite=100");
  const { elements }: { elements: DecisionRegistreApi[]; total: number } = reponse.ok
    ? await reponse.json()
    : { elements: [], total: 0 };

  const decisions: DecisionRegistreVue[] = elements.map((d) => ({
    decisionId: d.decision_id,
    societaireId: d.societaire_id,
    societaireNom: d.societaire_nom,
    agence: d.agence,
    resultat: d.resultat,
    horodatage: d.horodatage,
    agentNom: d.agent_nom,
  }));

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />
      <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-4 px-6 py-6">
        <h1 className="font-serif-title text-lg font-semibold text-neutre-950">
          Registre des décisions
        </h1>
        <RegistreDecisions decisions={decisions} />
      </main>
    </div>
  );
}
