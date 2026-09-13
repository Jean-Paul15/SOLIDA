"use client";

import { useRouter } from "next/navigation";
import { PartyPopper } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDemande } from "@/lib/demande-context";

export default function ConfirmationPage() {
  const router = useRouter();
  const { reinitialiser } = useDemande();

  function terminer() {
    reinitialiser();
    router.push("/");
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center justify-center px-6 py-10 text-center">
      <PartyPopper className="size-16 text-solida-teal-700" strokeWidth={1.5} />
      <h1 className="mt-6 text-2xl font-semibold text-balance">C&apos;est parti !</h1>
      <p className="mt-3 text-base text-muted-foreground text-balance">
        Votre demande a bien été transmise à votre agent. Il l&apos;examinera et vous recontactera
        prochainement.
      </p>
      <div className="mt-10 w-full">
        <Button onClick={terminer}>Terminer</Button>
      </div>
    </div>
  );
}
