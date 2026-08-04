"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { SyntheseGroupe } from "@/lib/contracts";
import { lireGroupe } from "@/lib/services/societaires";

const LIBELLE_ROLE: Record<string, string> = {
  membre: "Membre",
  presidente: "Présidente",
  tresoriere: "Trésorière",
  secretaire: "Secrétaire",
};

const LIBELLE_STATUT_CREDIT: Record<string, string> = {
  aucun_credit: "Aucun crédit",
  en_cours: "En cours",
  solde: "Soldé",
  en_souffrance: "En souffrance",
};

interface GroupeCautionDialogProps {
  societaireId: string;
}

export function GroupeCautionDialog({ societaireId }: GroupeCautionDialogProps) {
  const router = useRouter();
  const [groupe, setGroupe] = useState<SyntheseGroupe | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);

  function surOuverture(ouvert: boolean) {
    if (!ouvert || groupe || enCours) return;
    setEnCours(true);
    setErreur(null);
    lireGroupe(societaireId)
      .then(setGroupe)
      .catch(() => setErreur("Le groupe de caution n'a pas pu être chargé."))
      .finally(() => setEnCours(false));
  }

  return (
    <Dialog onOpenChange={surOuverture}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Voir le groupe
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[560px] gap-4 overflow-y-auto sm:max-w-[720px]">
        {enCours && (
          <div className="flex flex-1 items-center justify-center gap-2 py-10 text-sm text-neutre-500">
            <Loader2 className="size-4 animate-spin" />
            Chargement du groupe…
          </div>
        )}

        {erreur && <p className="py-10 text-center text-sm text-decision-refus">{erreur}</p>}

        {groupe && (
          <>
            <DialogHeader>
              <DialogTitle>{groupe.nom_groupe}</DialogTitle>
              <DialogDescription>
                Créé le{" "}
                {new Date(groupe.date_creation).toLocaleDateString("fr-FR", {
                  month: "long",
                  year: "numeric",
                })}{" "}
                · {groupe.taille_actuelle} membres
              </DialogDescription>
            </DialogHeader>

            <div className="flex items-center gap-2">
              <span className="text-sm text-neutre-500">Taux de remboursement collectif</span>
              <span className="font-mono text-lg text-neutre-950">
                {groupe.taux_remboursement_groupe !== null
                  ? `${Math.round(groupe.taux_remboursement_groupe * 100)}%`
                  : "—"}
              </span>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Membre</TableHead>
                  <TableHead>Rôle</TableHead>
                  <TableHead>Ancienneté</TableHead>
                  <TableHead>Statut crédit</TableHead>
                  <TableHead>Caution appelée</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {groupe.membres.map((m) => (
                  <TableRow
                    key={m.societaire_id}
                    onClick={() => router.push(`/societaires/${m.societaire_id}`)}
                    className={
                      m.societaire_id === societaireId
                        ? "cursor-pointer bg-solida-teal-50"
                        : "cursor-pointer"
                    }
                  >
                    <TableCell>{m.nom_complet}</TableCell>
                    <TableCell>{LIBELLE_ROLE[m.role]}</TableCell>
                    <TableCell>{Math.floor(m.anciennete_mois / 12)} an(s)</TableCell>
                    <TableCell>
                      <Badge
                        variant={m.statut_credit === "en_souffrance" ? "destructive" : "secondary"}
                      >
                        {LIBELLE_STATUT_CREDIT[m.statut_credit]}
                      </Badge>
                    </TableCell>
                    <TableCell>{m.caution_appelee ? "Oui" : "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="flex justify-between border-t border-neutre-200 pt-3 text-sm text-neutre-500">
              <span>{groupe.nb_cycles_completes} cycle(s) menés à terme</span>
              <span>{groupe.nb_sorties_12m} sortie(s) sur 12 mois</span>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
