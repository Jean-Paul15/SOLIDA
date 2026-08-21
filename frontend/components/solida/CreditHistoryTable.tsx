import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { CreditResume, ProduitCreditApi } from "@/lib/contracts";
import { formatAmount } from "@/lib/format";
import { LABEL_STATUT_CREDIT } from "@/lib/labels";
import { findProduit } from "@/lib/produits";

interface CreditHistoryTableProps {
  historique: CreditResume[];
  produits: ProduitCreditApi[];
}

export function CreditHistoryTable({ historique, produits }: CreditHistoryTableProps) {
  if (historique.length === 0) {
    return (
      <p className="text-sm text-neutre-500">
        Premier crédit : ce sociétaire n&rsquo;a pas d&rsquo;historique d&rsquo;emprunt.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Date de déblocage</TableHead>
          <TableHead>Produit</TableHead>
          <TableHead>Montant octroyé</TableHead>
          <TableHead>Durée</TableHead>
          <TableHead>Cycle</TableHead>
          <TableHead>Statut</TableHead>
          <TableHead>Capital restant dû</TableHead>
          <TableHead>Retard maximal</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {historique.map((c) => (
          <TableRow key={c.credit_id}>
            <TableCell>{new Date(c.date_deblocage).toLocaleDateString("fr-FR")}</TableCell>
            <TableCell>{findProduit(produits, c.produit_id)?.libelle ?? c.produit_id}</TableCell>
            <TableCell className="text-right font-mono">
              {formatAmount(c.montant_octroye)}
            </TableCell>
            <TableCell>{c.duree_mois} mois</TableCell>
            <TableCell>{c.numero_cycle}</TableCell>
            <TableCell>
              <Badge variant={c.statut === "en_souffrance" ? "destructive" : "secondary"}>
                {LABEL_STATUT_CREDIT[c.statut]}
              </Badge>
            </TableCell>
            <TableCell className="text-right font-mono">
              {formatAmount(c.capital_restant_du)}
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
  );
}
