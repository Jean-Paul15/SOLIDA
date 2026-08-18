import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { SESSION_COOKIE } from "@/lib/session";

const BACKEND_INTERNAL_URL = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

const ROUTES_PROTEGEES = [
  "/",
  "/societaires",
  "/scoring",
  "/registre",
  "/parametrage",
  "/changer-mot-de-passe",
];

function toLogin(request: NextRequest): NextResponse {
  const url = request.nextUrl.clone();
  url.pathname = "/connexion";
  url.searchParams.set("redirect", request.nextUrl.pathname);
  return NextResponse.redirect(url);
}

export async function proxy(request: NextRequest): Promise<NextResponse> {
  const { pathname } = request.nextUrl;
  const isProtected = ROUTES_PROTEGEES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const token = request.cookies.get(SESSION_COOKIE);
  if (!token) {
    return toLogin(request);
  }

  // La seule présence du cookie ne prouve rien (un cookie forgé de même nom suffirait) : sa
  // validité doit être vérifiée auprès du backend avant de laisser passer une page protégée.
  const verification = await fetch(`${BACKEND_INTERNAL_URL}/api/v1/auth/moi`, {
    headers: { cookie: `${SESSION_COOKIE}=${token.value}` },
  }).catch(() => null);

  if (!verification || !verification.ok) {
    return toLogin(request);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/societaires/:path*",
    "/scoring/:path*",
    "/registre/:path*",
    "/parametrage/:path*",
    "/changer-mot-de-passe",
  ],
};
