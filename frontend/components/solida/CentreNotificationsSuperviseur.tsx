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
import type { AgentAgenceApi, DemandeSocietaireApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { LABEL_OBJET_CREDIT } from "@/lib/labels";
import { useApiErrorToast } from "@/lib/services/error-service";
import {
  assignNotification,
  fetchAgentsAgence,
  fetchNotifications,
} from "@/lib/services/notifications";

const INTERVALLE_RAFRAICHISSEMENT_MS = 45_000;

interface CentreNotificationsSuperviseurProps {
  initial: DemandeSocietaireApi[];
}

/** Le superviseur répartit les demandes non assignées entre les agents — il ne tranche pas
 * lui-même le score (ce n'est pas son rôle), il n'a donc pas accès à `ScoringResultView` comme
 * `CentreNotificationsAgent`. Un superviseur d'agence ne voit qu'une seule agence, mais un
 * superviseur réseau peut voir des demandes de plusieurs agences dans la même liste : la liste
 * d'agents proposée est donc chargée par agence (celle de la ligne courante), pas une seule
 * fois globalement. */
export function CentreNotificationsSuperviseur({ initial }: CentreNotificationsSuperviseurProps) {
  const [notifications, setNotifications] = useState(initial);
  const [agentsParAgence, setAgentsParAgence] = useState<Record<string, AgentAgenceApi[]>>({});
  const [selection, setSelection] = useState<Record<string, string>>({});
  const [enCours, setEnCours] = useState<string | null>(null);
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

  return (
    <div className="flex flex-col gap-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Reçue le</TableHead>
            <TableHead>Sociétaire</TableHead>
            <TableHead>Agence</TableHead>
            <TableHead>Montant</TableHead>
            <TableHead>Objet</TableHead>
            <TableHead>Assigner à</TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {notifications.map((n) => {
            const agentsDeCetteAgence = agentsParAgence[n.agence_id] ?? [];
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
                <TableCell>{LABEL_OBJET_CREDIT[n.objet_credit]}</TableCell>
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
