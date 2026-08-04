import { EnTete } from "@/components/solida/EnTete";
import { RegistreDecisions } from "@/components/solida/RegistreDecisions";
import type { DecisionRegistreVue } from "@/lib/mocks/decisions";
import { listerDecisions } from "@/lib/mocks/decisions";
import { societaires } from "@/lib/mocks/societaires";
import { lireSession } from "@/lib/session";

export default async function PageRegistre() {
  const session = await lireSession();

  const decisions: DecisionRegistreVue[] = listerDecisions().flatMap((d) => {
    const fiche = societaires[d.societaireId];
    if (!fiche) return [];
    return [
      {
        ...d,
        societaireNom: fiche.dossier.identite.nom_complet,
        agence: fiche.dossier.identite.agence,
      },
    ];
  });

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
