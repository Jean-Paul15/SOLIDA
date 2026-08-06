import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { EnTete } from "@/components/solida/EnTete";
import { FicheApercu } from "@/components/solida/FicheApercu";
import { FicheActions } from "@/components/solida/FicheActions";
import { fetchBackend } from "@/lib/backend";
import type { FicheJustification, ProduitCreditApi } from "@/lib/contracts";
import { exigerMotDePasseAJour, lireSession, redirigerSiNonAuthentifie } from "@/lib/session";

const VERSION_APPLICATION = "solida-frontend-0.1.0";

interface PageFicheProps {
  params: Promise<{ id: string }>;
}

export default async function PageFiche({ params }: PageFicheProps) {
  const { id: decisionId } = await params;
  const [reponse, reponseProduits] = await Promise.all([
    fetchBackend(`/api/v1/scoring/${decisionId}/fiche`),
    fetchBackend("/api/v1/produits"),
  ]);
  redirigerSiNonAuthentifie(reponse);
  if (!reponse.ok) notFound();
  const ficheData: FicheJustification = await reponse.json();
  const produits: ProduitCreditApi[] = reponseProduits.ok ? await reponseProduits.json() : [];

  const session = await lireSession();
  exigerMotDePasseAJour(session);

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
          <FicheApercu
            fiche={ficheData}
            versionApplication={VERSION_APPLICATION}
            produits={produits}
          />
        </div>
        <FicheActions decisionId={decisionId} />
      </main>
    </div>
  );
}
