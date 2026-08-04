import { NextResponse } from "next/server";
import { rechercherSocietaires } from "@/lib/mocks/societaires";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const terme = url.searchParams.get("terme") ?? "";
  const limite = Number(url.searchParams.get("limite") ?? "10");

  if (terme.length < 2) {
    return NextResponse.json({ elements: [], total: 0 });
  }

  const resultats = rechercherSocietaires(terme);
  return NextResponse.json({
    elements: resultats.slice(0, limite),
    total: resultats.length,
  });
}
