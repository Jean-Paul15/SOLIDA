"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ResumeDemandeSocietaire } from "@/components/solida/ResumeDemandeSocietaire";
import { ScoringResultView } from "@/components/solida/ScoringResultView";
import type { AgentAgenceApi, DemandeSocietaireApi, ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { LABEL_OBJET_CREDIT, LABEL_TRANCHE, TRANCHE_COLOR } from "@/lib/labels";
import { findProduit } from "@/lib/produits";
import { useApiErrorToast } from "@/lib/services/error-service";
import {
  assignNotification,
  fetchAgentsAgence,
  fetchNotifications,
} from "@/lib/services/notifications";

const INTERVALLE_RAFRAICHISSEMENT_MS = 45_000;

interface CentreNotificationsSuperviseurProps {
  initial: DemandeSocietaireApi[];
  produits: ProduitCreditApi[];
}

/** Le superviseur répartit les demandes non assignées entre les agents — il ne tranche pas
 * lui-même le score (ce n'est pas son rôle), donc pas de bouton confirmer/annuler comme
 * `CentreNotificationsAgent`. Mais il doit pouvoir voir ce que le modèle recommande avant de
 * choisir à qui assigner : la colonne « Décision » affiche tranche et score en direct, et
 * ouvre le détail complet (jauge, facteurs, conditions de réexamen) en lecture seule. Un
 * superviseur d'agence ne voit qu'une seule agence, mais un superviseur réseau peut voir des
 * demandes de plusieurs agences dans la même liste : la liste d'agents proposée est donc
 * chargée par agence (celle de la ligne courante), pas une seule fois globalement. */
export function CentreNotificationsSuperviseur({
  initial,
  produits,
}: CentreNotificationsSuperviseurProps) {
  const [notifications, setNotifications] = useState(initial);
  const [agentsParAgence, setAgentsParAgence] = useState<Record<string, AgentAgenceApi[]>>({});
  const [selection, setSelection] = useState<Record<string, string>>({});
  const [enCours, setEnCours] = useState<string | null>(null);
  const [ouverte, setOuverte] = useState<string | null>(null);
  const afficherErreur = useApiErrorToast();

  useEffect(() => {
    const intervalle = setInterval(() => {
      fetchNotifications(50)
        .then((page) => setNotifications(page.elements))
        .catch(() => {
          // Silencieux : le prochain intervalle retentera.
        });
    }, INTERVALLE_RAFRAICHISSEMENT_MS);
    return () => clearInterval(intervalle);
  }, []);

  useEffect(() => {
    const agencesAChercher = [...new Set(notifications.map((n) => n.agence_id))].filter(
      (agence) => !(agence in agentsParAgence)
    );
    if (agencesAChercher.length === 0) return;
    Promise.all(
      agencesAChercher.map((agence) =>
        fetchAgentsAgence(agence).then((agents) => [agence, agents] as const)
      )
    )
      .then((paires) => {
        setAgentsParAgence((prev) => ({ ...prev, ...Object.fromEntries(paires) }));
      })
      .catch((erreur) => afficherErreur(erreur, "Impossible de charger la liste des agents."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [notifications]);

  async function assigner(notification: DemandeSocietaireApi) {
    const agentId = selection[notification.demande_id];
    if (!agentId) return;
    setEnCours(notification.demande_id);
    try {
      await assignNotification(notification.demande_id, agentId);
      setNotifications((prev) => prev.filter((n) => n.demande_id !== notification.demande_id));
      const agent = agentsParAgence[notification.agence_id]?.find((a) => a.id === agentId);
      toast.success(`Demande assignée à ${agent?.nom_complet ?? "l'agent choisi"}.`);
    } catch (erreur) {
      afficherErreur(erreur, "Impossible d'assigner cette demande.");
    } finally {
      setEnCours(null);
    }
  }

  const active = notifications.find((n) => n.demande_id === ouverte);

  if (active) {
    return (
      <div className="flex flex-col gap-4">
        <Button variant="outline" size="sm" onClick={() => setOuverte(null)} className="w-fit">
          Retour à la liste
        </Button>
        <ResumeDemandeSocietaire demande={active} produits={produits} />
        <ScoringResultView result={active.resultat} isPreview readOnly />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Reçue le</TableHead>
            <TableHead>Sociétaire</TableHead>
            <TableHead>Agence</TableHead>
            <TableHead>Montant</TableHead>
            <TableHead>Produit</TableHead>
            <TableHead>Objet</TableHead>
            <TableHead>Durée</TableHead>
            <TableHead>Décision du modèle</TableHead>
            <TableHead>Assigner à</TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {notifications.map((n) => {
            const agentsDeCetteAgence = agentsParAgence[n.agence_id] ?? [];
            const couleurs = TRANCHE_COLOR[n.resultat.tranche];
            return (
              <TableRow key={n.demande_id}>
                <TableCell>
                  {new Date(n.cree_le).toLocaleString("fr-FR", {
                    dateStyle: "short",
                    timeStyle: "short",
                  })}
                </TableCell>
                <TableCell>{n.societaire_nom}</TableCell>
                <TableCell>{n.agence_id}</TableCell>
                <TableCell className="text-right font-mono">
                  {formatAmount(n.montant_demande)}
                </TableCell>
                <TableCell>
                  {findProduit(produits, n.produit_id)?.libelle ?? n.produit_id}
                </TableCell>
                <TableCell>{LABEL_OBJET_CREDIT[n.objet_credit]}</TableCell>
                <TableCell>{n.duree_mois} mois</TableCell>
                <TableCell>
                  <button
                    type="button"
                    onClick={() => setOuverte(n.demande_id)}
                    aria-label={`Voir le détail de la décision : ${LABEL_TRANCHE[n.resultat.tranche]}, score ${Math.round(n.resultat.score)}`}
                    className={`flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-solida-teal-600 ${couleurs.text} ${couleurs.background}`}
                  >
                    {LABEL_TRANCHE[n.resultat.tranche]}
                    <span className="font-mono">{Math.round(n.resultat.score)}</span>
                  </button>
                </TableCell>
                <TableCell>
                  <Select
                    value={selection[n.demande_id]}
                    onValueChange={(v) => setSelection((prev) => ({ ...prev, [n.demande_id]: v }))}
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Choisir un agent" />
                    </SelectTrigger>
                    <SelectContent>
                      {agentsDeCetteAgence.map((a) => (
                        <SelectItem key={a.id} value={a.id}>
                          {a.nom_complet}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    disabled={!selection[n.demande_id]}
                    loading={enCours === n.demande_id}
                    onClick={() => assigner(n)}
                  >
                    Assigner
                  </Button>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {notifications.length === 0 && (
        <p className="py-8 text-center text-sm text-neutre-500">
          Aucune demande à répartir pour le moment.
        </p>
      )}
    </div>
  );
}
