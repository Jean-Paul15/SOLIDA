"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { ResumeDemandeSocietaire } from "@/components/solida/ResumeDemandeSocietaire";
import { ScoringResultView } from "@/components/solida/ScoringResultView";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { DemandeSocietaireApi, ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { LABEL_OBJET_CREDIT } from "@/lib/labels";
import { findProduit } from "@/lib/produits";
import { useApiErrorToast } from "@/lib/services/error-service";
import { archiveNotification, fetchNotifications } from "@/lib/services/notifications";
import { confirmDecision } from "@/lib/services/scoring";

const INTERVALLE_RAFRAICHISSEMENT_MS = 45_000;

interface CentreNotificationsAgentProps {
  initial: DemandeSocietaireApi[];
  produits: ProduitCreditApi[];
}

export function CentreNotificationsAgent({ initial, produits }: CentreNotificationsAgentProps) {
  const [notifications, setNotifications] = useState(initial);
  const [ouverte, setOuverte] = useState<string | null>(null);
  const [enCours, setEnCours] = useState(false);
  const router = useRouter();
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

  async function confirmer(notification: DemandeSocietaireApi) {
    setEnCours(true);
    try {
      const decision = await confirmDecision({
        societaire_id: notification.societaire_id,
        produit_id: notification.produit_id,
        montant_demande: notification.montant_demande,
        duree_demandee_mois: notification.duree_mois,
        objet_credit: notification.objet_credit,
      });
      await archiveNotification(notification.demande_id);
      router.push(`/scoring/${decision.decision_id}`);
    } catch (erreur) {
      afficherErreur(erreur, "Impossible d'enregistrer la décision.");
    } finally {
      setEnCours(false);
    }
  }

  async function ecarter(notification: DemandeSocietaireApi) {
    try {
      await archiveNotification(notification.demande_id);
      setNotifications((prev) => prev.filter((n) => n.demande_id !== notification.demande_id));
      setOuverte(null);
      toast.info("Notification écartée.");
    } catch (erreur) {
      afficherErreur(erreur, "Impossible d'écarter cette notification.");
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
        <ScoringResultView
          result={active.resultat}
          isPreview
          onConfirm={() => confirmer(active)}
          onCancel={() => ecarter(active)}
          confirmationInProgress={enCours}
        />
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
            <TableHead>Montant</TableHead>
            <TableHead>Produit</TableHead>
            <TableHead>Objet</TableHead>
            <TableHead>Durée</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {notifications.map((n) => (
            <TableRow
              key={n.demande_id}
              onClick={() => setOuverte(n.demande_id)}
              className="cursor-pointer"
            >
              <TableCell>
                {new Date(n.cree_le).toLocaleString("fr-FR", {
                  dateStyle: "short",
                  timeStyle: "short",
                })}
              </TableCell>
              <TableCell>{n.societaire_nom}</TableCell>
              <TableCell className="text-right font-mono">
                {formatAmount(n.montant_demande)}
              </TableCell>
              <TableCell>{findProduit(produits, n.produit_id)?.libelle ?? n.produit_id}</TableCell>
              <TableCell>{LABEL_OBJET_CREDIT[n.objet_credit]}</TableCell>
              <TableCell>{n.duree_mois} mois</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {notifications.length === 0 && (
        <p className="py-8 text-center text-sm text-neutre-500">
          Aucune demande ne vous est assignée pour le moment.
        </p>
      )}
    </div>
  );
}
