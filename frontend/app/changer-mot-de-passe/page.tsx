import { Header } from "@/components/solida/Header";
import { ChangePasswordForm } from "@/components/solida/ChangePasswordForm";
import { readSession } from "@/lib/session";

export default async function PageChangementMotDePasse() {
  const session = await readSession();

  return (
    <div className="flex min-h-screen flex-col">
      <Header agence={session?.agence} userName={session?.name} role={session?.role} />
      <main className="mx-auto flex w-full max-w-[420px] flex-1 flex-col justify-center gap-6 px-6 py-6">
        <div className="flex flex-col gap-1">
          <h1 className="font-serif-title text-lg font-semibold text-neutre-950">
            Changement de mot de passe requis
          </h1>
          <p className="text-sm text-neutre-500">
            Le mot de passe attribué à la création de ce compte doit être changé avant tout accès
            aux autres écrans.
          </p>
        </div>
        <ChangePasswordForm />
      </main>
    </div>
  );
}
