import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { PolitiqueCredit } from "@/components/solida/PolitiqueCredit";
import { fetchBackend } from "@/lib/backend";
import type { ConfigurationGrilleApi, DecisionRegistreApi } from "@/lib/contracts";
import { canAccessCreditPolicy } from "@/lib/roles";
import { readSession, redirectIfUnauthenticated } from "@/lib/session";

export default async function PageGrille() {
  const session = await readSession();
  if (!canAccessCreditPolicy(session?.role)) {
    redirect("/acces-refuse");
  }

  const [gridResponse, registerResponse] = await Promise.all([
    fetchBackend("/api/v1/parametrage/grille"),
    fetchBackend("/api/v1/registre?limite=50"),
  ]);
  redirectIfUnauthenticated(gridResponse);
  redirectIfUnauthenticated(registerResponse);

  const initialConfiguration: ConfigurationGrilleApi | null = gridResponse.ok
    ? await gridResponse.json()
    : null;
  const historicalScores: number[] = registerResponse.ok
    ? ((await registerResponse.json()) as { elements: DecisionRegistreApi[] }).elements.map(
        (d) => d.resultat.score
      )
    : [];
  return (
    <main className="mx-auto flex w-full max-w-[1200px] flex-1 flex-col gap-4 px-6 py-6">
      <Link
        href="/"
        className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
      >
        <ArrowLeft className="size-4" />
        Retour à la recherche
      </Link>
      <div>
        <h1 className="font-serif-title text-lg font-semibold text-neutre-950">
          Politique de crédit
        </h1>
        <p className="text-sm text-neutre-500">
          Seuils de décision et simulation d&rsquo;impact sur le portefeuille. Le plafond
          institutionnel unique est de 100&nbsp;000&nbsp;000 FCFA ; aucun plafond n&rsquo;est défini
          par produit.
        </p>
      </div>
      {initialConfiguration ? (
        <PolitiqueCredit
          initialConfiguration={initialConfiguration}
          historicalScores={historicalScores}
          role={session?.role}
        />
      ) : (
        <p className="text-sm text-neutre-500">
          Le paramétrage de la grille est réservé à la supervision, à l&rsquo;audit et à
          l&rsquo;administration.
        </p>
      )}
    </main>
  );
}
