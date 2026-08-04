import { NextResponse } from "next/server";
import type { FicheJustification } from "@/lib/contracts";
import { societaires } from "@/lib/mocks/societaires";
import { lireResultat } from "@/lib/mocks/scoring";
import { lireSession } from "@/lib/session";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const fiche = societaires[id];
  const resultat = lireResultat(id);

  if (!fiche || !resultat) {
    return NextResponse.json(
      { code: "introuvable", message: "Aucun résultat de scoring disponible pour ce sociétaire." },
      { status: 404 }
    );
  }

  const session = await lireSession();
  const favorables = resultat.decomposition.filter((c) => c.sens === "favorable").slice(0, 5);
  const defavorables = resultat.decomposition.filter((c) => c.sens === "defavorable").slice(0, 5);

  const reponse: FicheJustification = {
    fiche_id: `fiche-${id}-${Date.now()}`,
    resultat,
    societaire_nom: fiche.dossier.identite.nom_complet,
    agence: fiche.dossier.identite.agence,
    agent_nom: session?.nom ?? "Agent",
    date_edition: new Date().toISOString(),
    facteurs_favorables: favorables,
    facteurs_defavorables: defavorables,
    conditions_reexamen: resultat.conditions_reexamen,
    mention_legale:
      "La décision finale relève de l'agent et du comité de crédit. Cette fiche restitue le calcul du système à titre d'aide à la décision.",
  };

  return NextResponse.json(reponse);
}
