import { AlertTriangle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { EnTete } from "@/components/solida/EnTete";
import { NouvelleDemandeSheet } from "@/components/solida/NouvelleDemandeSheet";
import { TrajectoireEpargne } from "@/components/solida/TrajectoireEpargne";
import { formaterMontant } from "@/lib/format";
import { societaires } from "@/lib/mocks/societaires";
import { lireSession } from "@/lib/session";

const LIBELLE_SEGMENT: Record<string, string> = {
  salarie: "Salarié",
  individuel: "Individuel",
  jeune: "Jeune",
  femme_gie: "Groupement",
  agricole: "Agricole",
};

const LIBELLE_NIVEAU_INSTRUCTION: Record<string, string> = {
  aucun: "Non renseigné",
  primaire: "Primaire",
  secondaire: "Secondaire",
  superieur: "Supérieur",
};

const LIBELLE_STATUT_CREDIT: Record<string, string> = {
  en_cours: "En cours",
  solde: "Solde",
  en_souffrance: "En souffrance",
  radie: "Radié",
  restructure: "Restructuré",
};

export default async function PageDossier({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const fiche = societaires[id];
  if (!fiche) notFound();

  const session = await lireSession();
  const { identite, activite, epargne, historique_credit, alertes } = fiche.dossier;
  const anciennete = `${Math.floor(identite.anciennete_mois / 12)} an(s) ${identite.anciennete_mois % 12} mois`;

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} />

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
          <NouvelleDemandeSheet
            societaireId={id}
            nomComplet={identite.nom_complet}
            activite={activite}
          />
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
            <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
              <span className="text-xs font-medium text-neutre-500">Profil</span>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-neutre-500">Âge</span>
                <span className="text-neutre-950">{identite.age} ans</span>
                <span className="text-neutre-500">Personnes à charge</span>
                <span className="text-neutre-950">{activite.nb_personnes_a_charge}</span>
                <span className="text-neutre-500">Niveau d&rsquo;instruction</span>
                <span className="text-neutre-950">
                  {LIBELLE_NIVEAU_INSTRUCTION[identite.niveau_instruction ?? "aucun"]}
                </span>
                <span className="text-neutre-500">Parts sociales</span>
                <span className="font-mono text-neutre-950">
                  {formaterMontant(activite.parts_sociales_montant)}
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
              <span className="text-xs font-medium text-neutre-500">Activité économique</span>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-neutre-500">Secteur</span>
                <span className="text-neutre-950">{activite.secteur}</span>
                <span className="text-neutre-500">Ancienneté de l&rsquo;activité</span>
                <span className="text-neutre-950">
                  {Math.floor(activite.anciennete_activite_mois / 12)} an(s)
                </span>
                <span className="text-neutre-500">Revenu mensuel déclaré</span>
                {activite.revenu_mensuel_declare ? (
                  <span className="font-mono text-neutre-950">
                    {formaterMontant(activite.revenu_mensuel_declare)}
                  </span>
                ) : (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="flex items-center gap-1 text-sm text-neutre-500 italic">
                        Non renseigné <AlertTriangle className="size-3.5 text-alerte" />
                      </span>
                    </TooltipTrigger>
                    <TooltipContent>
                      Ce champ est absent du dossier et sera imputé lors du scoring, ce qui réduit
                      la précision.
                    </TooltipContent>
                  </Tooltip>
                )}
                <span className="text-neutre-500">Capacité de remboursement estimée</span>
                <span className="font-mono text-neutre-950">
                  {formaterMontant(activite.capacite_remboursement_estimee)}
                </span>
              </div>
            </div>
          </div>

          <div className="col-span-4">
            <TrajectoireEpargne epargne={epargne} />
          </div>

          <div className="col-span-3">
            {identite.segment === "femme_gie" && fiche.groupe ? (
              <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
                <span className="text-xs font-medium text-neutre-500">Groupe de caution</span>
                <span className="text-sm font-medium text-neutre-950">
                  {fiche.groupe.nom_groupe}
                </span>
                {fiche.groupe.taux_remboursement_groupe !== null ? (
                  <span className="font-mono text-lg text-neutre-950">
                    {Math.round(fiche.groupe.taux_remboursement_groupe * 100)}%
                  </span>
                ) : (
                  <span className="text-sm text-neutre-500">
                    Le groupe ne dispose pas encore d&rsquo;un historique de remboursement
                    suffisant. Le scoring s&rsquo;appuiera sur le profil individuel.
                  </span>
                )}
              </div>
            ) : (
              <div className="flex flex-col gap-2 rounded-lg border border-neutre-200 p-4">
                <span className="text-xs font-medium text-neutre-500">Épargne disponible</span>
                <span className="font-mono text-lg text-neutre-950">
                  {formaterMontant(epargne.solde_moyen_6m)}
                </span>
                <span className="text-xs text-neutre-500">
                  Garantie de droit commun sur ce dossier.
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-xs font-medium text-neutre-500">Historique de crédit</span>
          {historique_credit.length === 0 ? (
            <p className="text-sm text-neutre-500">
              Premier crédit — ce sociétaire n&rsquo;a pas d&rsquo;historique d&rsquo;emprunt.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date de déblocage</TableHead>
                  <TableHead>Montant octroyé</TableHead>
                  <TableHead>Durée</TableHead>
                  <TableHead>Cycle</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Capital restant dû</TableHead>
                  <TableHead>Retard maximal</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {historique_credit.map((c) => (
                  <TableRow key={c.credit_id}>
                    <TableCell>{new Date(c.date_deblocage).toLocaleDateString("fr-FR")}</TableCell>
                    <TableCell className="text-right font-mono">
                      {formaterMontant(c.montant_octroye)}
                    </TableCell>
                    <TableCell>{c.duree_mois} mois</TableCell>
                    <TableCell>{c.numero_cycle}</TableCell>
                    <TableCell>
                      <Badge variant={c.statut === "en_souffrance" ? "destructive" : "secondary"}>
                        {LIBELLE_STATUT_CREDIT[c.statut]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formaterMontant(c.capital_restant_du)}
                    </TableCell>
                    <TableCell
                      className={
                        c.max_jours_retard > 90
                          ? "text-decision-refus"
                          : c.max_jours_retard > 0
                            ? "text-alerte"
                            : "text-neutre-700"
                      }
                    >
                      {c.max_jours_retard} jour(s)
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
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
