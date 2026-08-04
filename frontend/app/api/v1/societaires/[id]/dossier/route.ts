import { NextResponse } from "next/server";
import { societaires } from "@/lib/mocks/societaires";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const fiche = societaires[id];

  if (!fiche) {
    return NextResponse.json(
      { code: "introuvable", message: "Aucun sociétaire ne correspond à cet identifiant." },
      { status: 404 }
    );
  }

  return NextResponse.json({
    ...fiche.dossier,
    groupe: fiche.groupe,
  });
}
