import { EnTete } from "@/components/solida/EnTete";
import { RechercheSocietaire } from "@/components/solida/RechercheSocietaire";
import { enforcePasswordUpToDate, readSession } from "@/lib/session";

export default async function PageRecherche() {
  const session = await readSession();
  enforcePasswordUpToDate(session);

  return (
    <div className="flex min-h-screen flex-col">
      <EnTete agence={session?.agence} utilisateur={session?.nom} role={session?.role} />
      <main className="flex-1 px-6">
        <RechercheSocietaire />
      </main>
    </div>
  );
}
