import { NextResponse } from "next/server";
import { societaires } from "@/lib/mocks/societaires";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const fiche = societaires[id];

  if (!fiche || fiche.dossier.identite.segment !== "femme_gie" || !fiche.groupe) {
    return NextResponse.json(
      { code: "sans_groupe", message: "Ce sociétaire n'appartient à aucun groupe actif." },
      { status: 404 }
    );
  }

  return NextResponse.json(fiche.groupe);
}
