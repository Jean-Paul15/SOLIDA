import { Header } from "@/components/solida/Header";
import { enforcePasswordUpToDate, readSession } from "@/lib/session";

/**
 * Le header ne doit jamais disparaître ni "recharger" pendant la navigation : en le
 * plaçant ici (plutôt que dans chaque `page.tsx`), il se rend dès que la session est
 * lue (rapide, un seul appel), pendant que `{children}` — le contenu propre à chaque
 * page, plus lourd — reste seul à afficher son `loading.tsx` le temps de résoudre.
 */
export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await readSession();
  enforcePasswordUpToDate(session);

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />
      <div className="flex flex-1 flex-col overflow-y-auto">{children}</div>
    </div>
  );
}
