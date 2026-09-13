import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { CentreNotifications } from "@/components/solida/CentreNotifications";
import { fetchBackend } from "@/lib/backend";
import type { PageNotificationsApi } from "@/lib/contracts";
import { redirectIfUnauthenticated } from "@/lib/session";

export default async function PageNotifications() {
  const response = await fetchBackend("/api/v1/notifications?limite=50");
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
      <CentreNotifications initial={elements} />
    </main>
  );
}
