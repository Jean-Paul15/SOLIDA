import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { CentreNotificationsAgent } from "@/components/solida/CentreNotificationsAgent";
import { CentreNotificationsSuperviseur } from "@/components/solida/CentreNotificationsSuperviseur";
import { fetchBackend } from "@/lib/backend";
import type { PageNotificationsApi } from "@/lib/contracts";
import { readSession, redirectIfUnauthenticated } from "@/lib/session";

export default async function PageNotifications() {
  const [response, session] = await Promise.all([
    fetchBackend("/api/v1/notifications?limite=50"),
    readSession(),
  ]);
  redirectIfUnauthenticated(response);
  const { elements }: PageNotificationsApi = response.ok
    ? await response.json()
    : { elements: [], total: 0 };

  return (
    <main className="mx-auto flex w-full max-w-[1440px] flex-1 flex-col gap-4 px-6 py-6">
      <Link
        href="/"
        className="flex items-center gap-1.5 text-sm text-neutre-500 hover:text-neutre-950"
      >
        <ArrowLeft className="size-4" />
        Retour à la recherche
      </Link>
      <h1 className="font-serif-title text-lg font-semibold text-neutre-950">
        Demandes des sociétaires
      </h1>
      {session?.role === "superviseur" ? (
        <CentreNotificationsSuperviseur initial={elements} />
      ) : (
        <CentreNotificationsAgent initial={elements} />
      )}
    </main>
  );
}
