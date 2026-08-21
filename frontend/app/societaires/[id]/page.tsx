import { AlertTriangle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/solida/Header";
import { SavingsMovements } from "@/components/solida/SavingsMovements";
import { NouvelleDemandeSheet } from "@/components/solida/NouvelleDemandeSheet";
import { EconomicActivityPanel } from "@/components/solida/EconomicActivityPanel";
import { GuaranteePanel } from "@/components/solida/GuaranteePanel";
import { ProfilePanel } from "@/components/solida/ProfilePanel";
import { CreditHistoryTable } from "@/components/solida/CreditHistoryTable";
import { fetchBackend } from "@/lib/backend";
import type { DossierSocietaire, ProduitCreditApi } from "@/lib/contracts";
import { canScore } from "@/lib/roles";
import {
  enforcePasswordUpToDate,
  readSession,
  redirectIfAccessDenied,
  redirectIfUnauthenticated,
} from "@/lib/session";

const LIBELLE_SEGMENT: Record<string, string> = {
  salarie: "Salarié",
  individuel: "Individuel",
  jeune: "Jeune",
  femme_gie: "Groupement",
  agricole: "Agricole",
};

export default async function PageDossier({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [reponse, reponseProduits] = await Promise.all([
    fetchBackend(`/api/v1/societaires/${id}/dossier`),
    fetchBackend("/api/v1/produits"),
  ]);
  redirectIfUnauthenticated(reponse);
  redirectIfAccessDenied(reponse);
  if (!reponse.ok) notFound();
  const dossier: DossierSocietaire = await reponse.json();
  const produits: ProduitCreditApi[] = reponseProduits.ok ? await reponseProduits.json() : [];

  const session = await readSession();
  enforcePasswordUpToDate(session);
  const { identite, activite, epargne, historique_credit, alertes, groupe } = dossier;
  const anciennete = `${Math.floor(identite.anciennete_mois / 12)} an(s) ${identite.anciennete_mois % 12} mois`;

  return (
    <div className="flex min-h-screen flex-col">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />

      <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-6 px-6 py-6">
        <Link
          href="/"
          className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
        >
          <ArrowLeft className="size-4" />
          Retour à la recherche
        </Link>

        <div className="flex h-[88px] items-center justify-between rounded-lg border border-neutre-200 px-4">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="text-base font-semibold text-neutre-950">
                {identite.nom_complet}
              </span>
              <Badge variant="secondary">{LIBELLE_SEGMENT[identite.segment]}</Badge>
            </div>
            <span className="text-xs text-neutre-500">
              N° {identite.numero_membre} · Sociétaire depuis{" "}
              {new Date(identite.date_adhesion).toLocaleDateString("fr-FR", {
                month: "long",
                year: "numeric",
              })}{" "}
              ({anciennete})
            </span>
            <span className="text-xs text-neutre-500">
              {identite.agence} · {activite.secteur}
            </span>
          </div>
          {canScore(session?.role) && (
            <NouvelleDemandeSheet
              societaireId={id}
              nomComplet={identite.nom_complet}
              activite={activite}
              produits={produits}
            />
          )}
        </div>

        {alertes.length > 0 && (
          <div className="flex flex-col gap-1">
            {alertes.map((a) => (
              <p key={a} className="flex items-center gap-2 text-sm text-alerte">
                <AlertTriangle className="size-4" />
                {a}
              </p>
            ))}
          </div>
        )}

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-5 flex flex-col gap-4">
            <ProfilePanel identite={identite} activite={activite} />
            <EconomicActivityPanel activite={activite} />
          </div>

          <div className="col-span-4">
            <SavingsMovements epargne={epargne} />
          </div>

          <div className="col-span-3">
            <GuaranteePanel
              segment={identite.segment}
              groupe={groupe}
              societaireId={id}
              epargne={epargne}
            />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-xs font-medium text-neutre-500">Historique de crédit</span>
          <CreditHistoryTable historique={historique_credit} produits={produits} />
        </div>

        <span className="text-xs text-neutre-500">
          Données consolidées le{" "}
          {new Date().toLocaleDateString("fr-FR", {
            day: "numeric",
            month: "long",
            year: "numeric",
          })}
          .
        </span>
      </main>
    </div>
  );
}
