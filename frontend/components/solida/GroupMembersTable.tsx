import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { MembreGroupe } from "@/lib/contracts";
import { GROUP_ROLE_LABEL, LABEL_STATUT_CREDIT_MEMBRE } from "@/lib/labels";

interface GroupMembersTableProps {
  members: MembreGroupe[];
  societaireId: string;
}

export function GroupMembersTable({ members, societaireId }: GroupMembersTableProps) {
  const router = useRouter();

  return (
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
        {members.map((member) => (
          <TableRow
            key={member.societaire_id}
            onClick={() => router.push(`/societaires/${member.societaire_id}`)}
            className={
              member.societaire_id === societaireId
                ? "cursor-pointer bg-solida-teal-50"
                : "cursor-pointer"
            }
          >
            <TableCell>{member.nom_complet}</TableCell>
            <TableCell>{GROUP_ROLE_LABEL[member.role]}</TableCell>
            <TableCell>{Math.floor(member.anciennete_mois / 12)} an(s)</TableCell>
            <TableCell>
              <Badge
                variant={member.statut_credit === "en_souffrance" ? "destructive" : "secondary"}
              >
                {LABEL_STATUT_CREDIT_MEMBRE[member.statut_credit]}
              </Badge>
            </TableCell>
            <TableCell>{member.caution_appelee ? "Oui" : "—"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
