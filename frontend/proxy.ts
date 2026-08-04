import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { SESSION_COOKIE } from "@/lib/session";

const ROUTES_PROTEGEES = ["/", "/societaires", "/scoring"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const estProtegee = ROUTES_PROTEGEES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  if (!estProtegee) {
    return NextResponse.next();
  }

  const session = request.cookies.get(SESSION_COOKIE);
  if (!session) {
    const url = request.nextUrl.clone();
    url.pathname = "/connexion";
    url.searchParams.set("redirect", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/", "/societaires/:path*", "/scoring/:path*"],
};
