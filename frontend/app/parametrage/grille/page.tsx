import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { EnTete } from "@/components/solida/EnTete";
import { GrilleParametrage } from "@/components/solida/GrilleParametrage";
import { fetchBackend } from "@/lib/backend";
import type {
  ConfigurationGrilleApi,
  DecisionRegistreApi,
  ProduitCreditApi,
} from "@/lib/contracts";
import { exigerMotDePasseAJour, lireSession, redirigerSiNonAuthentifie } from "@/lib/session";

export default async function PageGrille() {
  const session = await lireSession();
  exigerMotDePasseAJour(session);

  const [reponseGrille, reponseRegistre, reponseProduits] = await Promise.all([
    fetchBackend("/api/v1/parametrage/grille"),
    fetchBackend("/api/v1/registre?limite=100"),
    fetchBackend("/api/v1/produits"),
  ]);
  redirigerSiNonAuthentifie(reponseGrille);
  redirigerSiNonAuthentifie(reponseRegistre);
  redirigerSiNonAuthentifie(reponseProduits);

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
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />
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
            Paramétrage de la grille de décision
          </h1>
          <p className="text-sm text-neutre-500">
            Ajuster les seuils sans réentraîner le modèle. L&rsquo;aperçu se recalcule sur
            l&rsquo;historique en direct.
          </p>
        </div>
        {configurationInitiale ? (
          <GrilleParametrage
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
    </div>
  );
}
