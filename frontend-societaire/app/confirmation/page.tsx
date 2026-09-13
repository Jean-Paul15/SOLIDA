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
    <div className="mx-auto flex min-h-dvh max-w-md flex-col items-center px-6 pt-16 text-center">
      <PartyPopper className="size-12 text-solida-teal-700" strokeWidth={1.5} />
      <h1 className="mt-5 text-xl font-semibold text-balance">C&apos;est parti !</h1>
      <p className="mt-2 text-base text-muted-foreground text-balance">
        Votre demande a bien été transmise à votre agent. Il l&apos;examinera et vous recontactera
        prochainement.
      </p>
      <div className="mt-7 w-full">
        <Button onClick={terminer}>Terminer</Button>
      </div>
    </div>
  );
}
