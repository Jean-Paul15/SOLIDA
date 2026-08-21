import { Header } from "@/components/solida/Header";
import { readSession } from "@/lib/session";

/**
 * Layout dédié (pas dans le groupe `(app)`) : cette page est l'échappatoire du
 * mot de passe par défaut, elle ne doit jamais déclencher elle-même
 * `enforcePasswordUpToDate` (boucle de redirection immédiate).
 */
export default async function ChangePasswordLayout({ children }: { children: React.ReactNode }) {
  const session = await readSession();

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />
      <div className="flex flex-1 flex-col overflow-y-auto">{children}</div>
    </div>
  );
}
