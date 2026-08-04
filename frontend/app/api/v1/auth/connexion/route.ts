import { NextResponse } from "next/server";
import { verifierIdentifiants } from "@/lib/mocks/agents";
import { creerSession } from "@/lib/session";

export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const identifiant = body?.identifiant;
  const motDePasse = body?.mot_de_passe;

  if (typeof identifiant !== "string" || typeof motDePasse !== "string") {
    return NextResponse.json(
      { code: "validation", message: "Identifiant et mot de passe requis." },
      { status: 400 }
    );
  }

  const agent = verifierIdentifiants(identifiant, motDePasse);
  if (!agent) {
    return NextResponse.json(
      { code: "authentification", message: "Identifiant ou mot de passe incorrect." },
      { status: 401 }
    );
  }

  await creerSession({ identifiant: agent.identifiant, nom: agent.nom, agence: agent.agence });
  return NextResponse.json({ nom: agent.nom, agence: agent.agence });
}
