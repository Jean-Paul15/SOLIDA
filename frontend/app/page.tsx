import { Header } from "@/components/solida/Header";
import { SocietaireSearch } from "@/components/solida/SocietaireSearch";
import { enforcePasswordUpToDate, readSession } from "@/lib/session";

export default async function PageRecherche() {
  const session = await readSession();
  enforcePasswordUpToDate(session);

  return (
    <div className="flex min-h-screen flex-col">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />
      <main className="flex-1 px-6">
        <SocietaireSearch />
      </main>
    </div>
  );
}
