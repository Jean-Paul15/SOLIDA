import { NextResponse } from "next/server";
import { detruireSession } from "@/lib/session";

export async function POST() {
  await detruireSession();
  return NextResponse.json({ statut: "ok" });
}
