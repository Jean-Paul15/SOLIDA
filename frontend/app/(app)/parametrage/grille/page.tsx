import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { redirect } from "next/navigation";
import { PolitiqueCredit } from "@/components/solida/PolitiqueCredit";
import { fetchBackend } from "@/lib/backend";
import type {
  ConfigurationGrilleApi,
  DecisionRegistreApi,
  ProduitCreditApi,
} from "@/lib/contracts";
import { canAccessCreditPolicy } from "@/lib/roles";
import { readSession, redirectIfUnauthenticated } from "@/lib/session";

export default async function PageGrille() {
  const session = await readSession();
  if (!canAccessCreditPolicy(session?.role)) {
    redirect("/acces-refuse");
  }

  const [reponseGrille, reponseRegistre, reponseProduits] = await Promise.all([
    fetchBackend("/api/v1/parametrage/grille"),
    fetchBackend("/api/v1/registre?limite=100"),
    fetchBackend("/api/v1/produits"),
  ]);
  redirectIfUnauthenticated(reponseGrille);
  redirectIfUnauthenticated(reponseRegistre);
  redirectIfUnauthenticated(reponseProduits);

  const configurationInitiale: ConfigurationGrilleApi | null = reponseGrille.ok
    ? await reponseGrille.json()
    : null;
  const scoresHistoriques: number[] = reponseRegistre.ok
    ? ((await reponseRegistre.json()) as { elements: DecisionRegistreApi[] }).elements.map(
        (d) => d.resultat.score
      )
    : [];
  const produits: ProduitCreditApi[] = reponseProduits.ok ? await reponseProduits.json() : [];

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
          Seuils de décision, plafonds par produit et simulation d&rsquo;impact sur le portefeuille.
        </p>
      </div>
      {configurationInitiale ? (
        <PolitiqueCredit
          configurationInitiale={configurationInitiale}
          scoresHistoriques={scoresHistoriques}
          role={session?.role}
          produits={produits}
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
