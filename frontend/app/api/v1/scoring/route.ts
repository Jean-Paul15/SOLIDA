import { NextResponse } from "next/server";
import type { EntreeScoring } from "@/lib/contracts";
import { enregistrerDecision } from "@/lib/mocks/decisions";
import { calculerScoring } from "@/lib/mocks/scoring";

export async function POST(request: Request) {
  const entree = (await request.json().catch(() => null)) as EntreeScoring | null;

  if (!entree?.societaire_id || !entree.montant_demande || !entree.duree_demandee_mois) {
    return NextResponse.json(
      { code: "validation", message: "Le montant et la durée sollicités sont obligatoires." },
      { status: 400 }
    );
  }

  try {
    const resultatSansId = calculerScoring(entree);
    const resultat = enregistrerDecision(entree.societaire_id, resultatSansId);
    return NextResponse.json(resultat, { status: 201 });
  } catch {
    return NextResponse.json(
      { code: "introuvable", message: "Aucun sociétaire ne correspond à cet identifiant." },
      { status: 404 }
    );
  }
}
